# Jarvis Discord Bot

Jarvis is a Discord bot that integrates with a custom OpenAPI-compliant LLM API. It enables users to interact with an advanced language model directly from Discord by mentioning the bot.

## Features

- **@Mention to Ask**: Users can mention `@jarvis` in any channel to ask questions.
- **Contextual Responses**: If the mention is a reply to another message, Jarvis includes the referenced message as context for more relevant answers.
- **Custom LLM Integration**: Connects to your specified OpenAPI-compatible LLM endpoint.

## Usage

1. **Ask a Question**  
   Mention the bot in your message:

```
@jarvis What is the capital of France?
```

2. **Contextual Question**  
   Reply to a message and mention the bot:

```
[Reply to a previous message]
@jarvis Can you explain this further?
```

Jarvis will use the replied-to message as additional context.

## Setup

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/jarvis-discord-bot.git
cd jarvis-discord-bot
```

2. **Install Dependencies**

```bash
npm install
```

3. **Configure Environment Variables**  
   Create a `.env` file with the following:

```
DISCORD_TOKEN=your-discord-bot-token
LLM_API_URL=https://your-llm-api-endpoint
LLM_API_KEY=your-llm-api-key
```

4. **Run the Bot**

```bash
npm start
```

## Configuration

- **LLM_API_URL**: The endpoint of your OpenAPI-compliant LLM.
- **LLM_API_KEY**: API key or token for authentication (if required).

## License

MIT License

---

_Jarvis is not affiliated with Discord or OpenAI._
