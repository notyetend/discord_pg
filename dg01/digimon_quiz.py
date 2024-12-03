import asyncio
from typing import Optional

import discord
from discord.ext import commands


class QuizView:
    """퀴즈 관련 UI를 관리하는 클래스"""

    @staticmethod
    async def send_quiz(channel: discord.TextChannel, user_id: int, question: str) -> None:
        """퀴즈 출제 메시지를 전송합니다."""
        quiz_embed = discord.Embed(
            title="🎯 진화 퀴즈!",
            description=f"다음 단계로 진화하기 위한 퀴즈입니다!\n\n**문제**: {question}",
            color=discord.Color.blue()
        )
        quiz_embed.add_field(
            name="답변 방법",
            value="채팅으로 답을 입력해주세요! (30초 안에 답변해야 합니다)",
            inline=False
        )

        await channel.send(embed=quiz_embed)

    @staticmethod
    async def send_timeout(channel: discord.TextChannel, user_id: int) -> None:
        """퀴즈 시간 초과 메시지를 전송합니다."""
        await channel.send(f"<@{user_id}> 시간이 초과되었습니다! 다시 도전해보세요.")

    @staticmethod
    async def send_already_active(channel: discord.TextChannel, user_id: int) -> None:
        """이미 진행 중인 퀴즈가 있다는 메시지를 전송합니다."""
        await channel.send(f"<@{user_id}> 이미 진행 중인 퀴즈가 있습니다!")

    @staticmethod
    async def send_correct_answer(channel: discord.TextChannel) -> None:
        """정답 메시지를 전송합니다."""
        success_embed = discord.Embed(
            title="🎉 정답입니다!",
            description="축하합니다! 다음 단계로 진화합니다!",
            color=discord.Color.green()
        )
        await channel.send(embed=success_embed)

    @staticmethod
    async def send_wrong_answer(channel: discord.TextChannel) -> None:
        """오답 메시지를 전송합니다."""
        fail_embed = discord.Embed(
            title="❌ 오답입니다!",
            description="다시 한번 도전해보세요!",
            color=discord.Color.red()
        )
        await channel.send(embed=fail_embed)


class QuizHandler:
    """퀴즈 관련 로직을 처리하는 클래스"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = QuizView()
        self.active_quizzes = {}  # user_id: quiz_info

    async def start_quiz(self, channel: discord.TextChannel, user_id: int,
                        question: str, answer: str, timeout_callback) -> bool:
        """새 퀴즈를 시작합니다."""
        if user_id in self.active_quizzes:
            await self.view.send_already_active(channel, user_id)
            return False

        await self.view.send_quiz(channel, user_id, question)

        timeout_task = asyncio.create_task(self._handle_timeout(
            user_id, channel, timeout_callback
        ))

        self.active_quizzes[user_id] = {
            'answer': answer,
            'channel_id': channel.id,
            'quiz_task': timeout_task
        }
        return True

    async def _handle_timeout(self, user_id: int, channel: discord.TextChannel,
                            timeout_callback) -> None:
        """퀴즈 타임아웃을 처리합니다."""
        await asyncio.sleep(30)
        if user_id in self.active_quizzes:
            await self.end_quiz(user_id)
            await self.view.send_timeout(channel, user_id)
            await timeout_callback(user_id)

    async def check_answer(self, user_id: int, channel_id: int,
                          answer: str) -> Optional[bool]:
        """사용자의 답변을 확인합니다."""
        quiz_info = self.active_quizzes.get(user_id)
        if not quiz_info or quiz_info['channel_id'] != channel_id:
            return None

        quiz_info['quiz_task'].cancel()
        is_correct = answer.strip().lower() == quiz_info['answer'].lower()
        await self.end_quiz(user_id)

        if is_correct:
            await self.view.send_correct_answer(
                self.bot.get_channel(channel_id)
            )
        else:
            await self.view.send_wrong_answer(
                self.bot.get_channel(channel_id)
            )

        return is_correct

    async def end_quiz(self, user_id: int) -> None:
        """진행 중인 퀴즈를 종료합니다."""
        if user_id in self.active_quizzes:
            del self.active_quizzes[user_id]