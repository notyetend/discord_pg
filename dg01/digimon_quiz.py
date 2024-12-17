
import asyncio
from typing import Optional

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
from discord import ButtonStyle, Interaction
from discord.ui import Button, View




class QuizModal(Modal):
    def __init__(self, question: str, correct_answer: str, callback):
        super().__init__(title="진화 퀴즈")
        self.correct_answer = correct_answer
        self.callback = callback
        
        # Add question display
        self.add_item(
            TextInput(
                label="문제",
                default=question,
                style=discord.TextStyle.paragraph,
                required=False
            )
        )
        
        # Add answer input
        self.add_item(
            TextInput(
                label="답변",
                placeholder="답을 입력하세요",
                style=discord.TextStyle.short,
                required=True,
                max_length=100
            )
        )

    async def on_submit(self, interaction: Interaction):
        answer = self.children[1].value.strip()
        is_correct = answer.lower() == self.correct_answer.lower()
        
        if is_correct:
            embed = discord.Embed(
                title="🎉 정답입니다!",
                description="축하합니다! 다음 단계로 진화합니다!",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ 오답입니다!",
                description="다시 한번 도전해보세요!",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)
        await self.callback(interaction.user.id, interaction.channel_id, answer)

class QuizView(View):
    def __init__(self, question: str, correct_answer: str, callback, timeout=30):
        super().__init__(timeout=timeout)
        self.question = question
        self.correct_answer = correct_answer
        self.callback = callback
        
        # Add answer button
        self.add_item(Button(
            label="답변하기",
            style=ButtonStyle.primary,
            custom_id="answer_quiz"
        ))
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.data["custom_id"] == "answer_quiz":
            modal = QuizModal(
                question=self.question,
                correct_answer=self.correct_answer,
                callback=self.callback
            )
            await interaction.response.send_modal(modal)
        return True


# Update QuizHandler class
class QuizHandler:
    def __init__(self, bot: commands.Bot, game_manager=None):
        self.bot = bot
        self.game_manager = game_manager
        self.active_quizzes = {}

    async def start_quiz(self, channel: discord.TextChannel, user_id: int,
                        question: str, answer: str, timeout_callback) -> bool:
        """새 퀴즈를 시작합니다."""
        if user_id in self.active_quizzes:
            embed = discord.Embed(
                title="⚠️ 진행 중인 퀴즈",
                description=f"<@{user_id}> 이미 진행 중인 퀴즈가 있습니다!",
                color=discord.Color.orange()
            )
            await channel.send(embed=embed)
            return False

        # Create and send quiz embed with button
        quiz_embed = discord.Embed(
            title="🎯 진화 퀴즈!",
            description="다음 단계로 진화하기 위한 퀴즈입니다!",
            color=discord.Color.blue()
        )
        
        quiz_view = QuizView(
            question=question,
            correct_answer=answer,
            callback=self.check_answer,
            timeout=30
        )
        
        message = await channel.send(embed=quiz_embed, view=quiz_view)
        
        # Set up timeout handling
        timeout_task = asyncio.create_task(self._handle_timeout(
            user_id, channel, timeout_callback, message
        ))

        self.active_quizzes[user_id] = {
            'answer': answer,
            'channel_id': channel.id,
            'quiz_task': timeout_task,
            'message': message
        }
        
        return True

    async def _handle_timeout(self, user_id: int, channel: discord.TextChannel,
                            timeout_callback, message: discord.Message) -> None:
        """퀴즈 타임아웃을 처리합니다."""
        await asyncio.sleep(30)
        if user_id in self.active_quizzes:
            await self.end_quiz(user_id)
            
            timeout_embed = discord.Embed(
                title="⏰ 시간 초과",
                description=f"<@{user_id}> 시간이 초과되었습니다! 다시 도전해보세요.",
                color=discord.Color.red()
            )
            
            # Disable the button view
            try:
                await message.edit(embed=timeout_embed, view=None)
            except discord.NotFound:
                pass
                
            await timeout_callback(user_id)

    async def check_answer(self, user_id: int, channel_id: int, answer: str) -> Optional[bool]:
        """사용자의 답변을 확인합니다."""
        quiz_info = self.active_quizzes.get(user_id)
        if not quiz_info or quiz_info['channel_id'] != channel_id:
            return None

        quiz_info['quiz_task'].cancel()
        is_correct = answer.strip().lower() == quiz_info['answer'].lower()

        session = await self.game_manager.get_session(user_id, channel_id)
        if is_correct:
            session.digimon.mark_quiz_passed()
        else:
            session.digimon.mark_quiz_failed()

        # Disable the button view
        try:
            await quiz_info['message'].edit(view=None)
        except discord.NotFound:
            pass
            
        await self.end_quiz(user_id)
        return is_correct

    async def end_quiz(self, user_id: int) -> None:
        """진행 중인 퀴즈를 종료합니다."""
        if user_id in self.active_quizzes:
            del self.active_quizzes[user_id]