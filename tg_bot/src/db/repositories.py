from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatMessage


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_message(
        self,
        chat_id: int,
        chat_title: str,
        user_id: int,
        user_name: str,
        message_text: str,
    ) -> None:
        message = ChatMessage(
            chat_id=str(chat_id),
            chat_title=chat_title,
            user_id=user_id,
            user_name=user_name,
            message_text=message_text,
        )
        self.session.add(message)
        await self.session.commit()
