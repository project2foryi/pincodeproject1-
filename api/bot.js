export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { message } = req.body;
    if (message && message.text) {
      const chatId = message.chat.id;
      const text = message.text;

      let replyText = `Aapne yeh PIN code bheja hai: ${text}. Jald hi iski details milengi!`;

      // Telegram par message wapas bhejne ki API request
      await fetch(`https://api.telegram.org/bot${process.env.BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId, text: replyText })
      });
    }
    return res.status(200).json({ status: 'success' });
  }
  return res.status(200).json({ status: 'Bot is active' });
}
