"""WebSocket 连接管理器 - 用于管理端结束考试时实时通知学生端"""
import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """管理每个考试的 WebSocket 连接"""

    def __init__(self):
        # exam_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, exam_id: int, websocket: WebSocket):
        """接受 WebSocket 连接并加入对应考试的连接池"""
        await websocket.accept()
        if exam_id not in self.active_connections:
            self.active_connections[exam_id] = set()
        self.active_connections[exam_id].add(websocket)

    def disconnect(self, exam_id: int, websocket: WebSocket):
        """断开连接并从连接池中移除"""
        if exam_id in self.active_connections:
            self.active_connections[exam_id].discard(websocket)
            if not self.active_connections[exam_id]:
                del self.active_connections[exam_id]

    async def broadcast_to_exam(self, exam_id: int, message: dict):
        """向指定考试的所有连接学生广播消息"""
        if exam_id not in self.active_connections:
            return
        dead = set()
        for ws in self.active_connections[exam_id]:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.add(ws)
        # 清理断开的连接
        for ws in dead:
            self.active_connections[exam_id].discard(ws)
        if not self.active_connections.get(exam_id):
            del self.active_connections[exam_id]

    def broadcast_to_exam_sync(self, exam_id: int, message: dict):
        """同步方式广播（从同步端点调用时使用）"""
        if exam_id not in self.active_connections:
            return
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行（uvicorn 环境），创建任务
                loop.create_task(self.broadcast_to_exam(exam_id, message))
            else:
                loop.run_until_complete(self.broadcast_to_exam(exam_id, message))
        except RuntimeError:
            # 没有事件循环，创建新的
            asyncio.run(self.broadcast_to_exam(exam_id, message))


# 全局单例
manager = ConnectionManager()
