import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from focus import FocusManager
from yougile_integration import YouGileIntegration
from opencode_integration import OpenCodeIntegration
from bot_config import BotConfig

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class OpenCodeBot:
    def __init__(self):
        self.config = BotConfig()
        self.focus = FocusManager()
        self.yougile = YouGileIntegration()
        self.opencode = OpenCodeIntegration()
        self.user_states = {}

    def is_allowed(self, user_id: int) -> bool:
        allowed = self.config.allowed_users
        return not allowed or user_id in allowed

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_allowed(update.effective_user.id):
            await update.message.reply_text("⛔ Доступ запрещён. Этот бот только для владельца.")
            return
        keyboard = [
            [InlineKeyboardButton("🎯 Фокус", callback_data="focus"),
             InlineKeyboardButton("📋 YouGile", callback_data="yougile")],
            [InlineKeyboardButton("🤖 OpenCode", callback_data="opencode"),
             InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👋 Привет! Я бот для управления OpenCode-агентами.\n\n"
            "Выберите раздел:",
            reply_markup=reply_markup
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if not self.is_allowed(query.from_user.id):
            await query.edit_message_text("⛔ Доступ запрещён. Этот бот только для владельца.")
            return

        if query.data == "focus":
            await self.show_focus_menu(query)
        elif query.data == "yougile":
            await self.show_yougile_menu(query)
        elif query.data == "opencode":
            await self.show_opencode_menu(query)
        elif query.data.startswith("focus_"):
            await self.handle_focus_action(query, context)
        elif query.data.startswith("yougile_"):
            await self.handle_yougile_action(query, context)
        elif query.data.startswith("opencode_"):
            await self.handle_opencode_action(query, context)

    async def show_focus_menu(self, query):
        keyboard = [
            [InlineKeyboardButton("📊 Текущий фокус", callback_data="focus_current")],
            [InlineKeyboardButton("➕ Добавить задачу", callback_data="focus_add")],
            [InlineKeyboardButton("✅ Завершить задачу", callback_data="focus_complete")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🎯 Меню фокуса:", reply_markup=reply_markup)

    async def show_yougile_menu(self, query):
        keyboard = [
            [InlineKeyboardButton("📋 Мои задачи", callback_data="yougile_tasks")],
            [InlineKeyboardButton("➕ Создать задачу", callback_data="yougile_create")],
            [InlineKeyboardButton("📊 Проекты", callback_data="yougile_projects")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📋 YouGile:", reply_markup=reply_markup)

    async def show_opencode_menu(self, query):
        keyboard = [
            [InlineKeyboardButton("🤖 Статус агентов", callback_data="opencode_status")],
            [InlineKeyboardButton("▶️ Запустить агента", callback_data="opencode_start")],
            [InlineKeyboardButton("⏹ Остановить агента", callback_data="opencode_stop")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🤖 OpenCode:", reply_markup=reply_markup)

    async def handle_focus_action(self, query, context):
        if query.data == "focus_current":
            tasks = self.focus.get_current_tasks()
            text = "📊 Текущий фокус:\n\n"
            for i, task in enumerate(tasks, 1):
                text += f"{i}. {task['title']}\n"
            await query.edit_message_text(text)
        elif query.data == "focus_add":
            self.user_states[query.from_user.id] = "waiting_focus_task"
            await query.edit_message_text("Введите название задачи:")
        elif query.data == "focus_complete":
            tasks = self.focus.get_current_tasks()
            keyboard = []
            for task in tasks:
                keyboard.append([InlineKeyboardButton(task['title'], callback_data=f"focus_done_{task['id']}")])
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="focus")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Выберите задачу для завершения:", reply_markup=reply_markup)

    async def handle_yougile_action(self, query, context):
        if query.data == "yougile_tasks":
            tasks = await self.yougile.get_tasks()
            text = "📋 Ваши задачи:\n\n"
            for i, task in enumerate(tasks[:10], 1):
                text += f"{i}. {task['title']} [{task['status']}]\n"
            await query.edit_message_text(text)
        elif query.data == "yougile_create":
            self.user_states[query.from_user.id] = "waiting_yougile_task"
            await query.edit_message_text("Введите название задачи:")
        elif query.data == "yougile_projects":
            projects = await self.yougile.get_projects()
            text = "📊 Проекты:\n\n"
            for i, proj in enumerate(projects, 1):
                text += f"{i}. {proj['title']}\n"
            await query.edit_message_text(text)

    async def handle_opencode_action(self, query, context):
        if query.data == "opencode_status":
            agents = await self.opencode.get_agents_status()
            text = "🤖 Статус агентов:\n\n"
            for agent in agents:
                status = "🟢" if agent['running'] else "🔴"
                text += f"{status} {agent['name']}\n"
            await query.edit_message_text(text)
        elif query.data == "opencode_start":
            agents = await self.opencode.get_agents_status()
            keyboard = []
            for agent in agents:
                if not agent['running']:
                    keyboard.append([InlineKeyboardButton(agent['name'], callback_data=f"opencode_run_{agent['id']}")])
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="opencode")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Выберите агента для запуска:", reply_markup=reply_markup)
        elif query.data == "opencode_stop":
            agents = await self.opencode.get_agents_status()
            keyboard = []
            for agent in agents:
                if agent['running']:
                    keyboard.append([InlineKeyboardButton(agent['name'], callback_data=f"opencode_stop_{agent['id']}")])
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="opencode")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Выберите агента для остановки:", reply_markup=reply_markup)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        if not self.is_allowed(user_id):
            await update.message.reply_text("⛔ Доступ запрещён. Этот бот только для владельца.")
            return
        text = update.message.text

        if user_id in self.user_states:
            state = self.user_states[user_id]

            if state == "waiting_focus_task":
                self.focus.add_task(text)
                await update.message.reply_text(f"✅ Задача добавлена: {text}")
                del self.user_states[user_id]

            elif state == "waiting_yougile_task":
                await self.yougile.create_task(text)
                await update.message.reply_text(f"✅ Задача создана в YouGile: {text}")
                del self.user_states[user_id]

    async def back_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("🎯 Фокус", callback_data="focus"),
             InlineKeyboardButton("📋 YouGile", callback_data="yougile")],
            [InlineKeyboardButton("🤖 OpenCode", callback_data="opencode"),
             InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "👋 Привет! Я бот для управления OpenCode-агентами.\n\n"
            "Выберите раздел:",
            reply_markup=reply_markup
        )

def main():
    bot = OpenCodeBot()
    application = Application.builder().token(bot.config.bot_token).build()

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.back_handler, pattern="^back$"))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
