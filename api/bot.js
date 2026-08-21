import fetch from 'node-fetch';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(200).json({ status: 'Bot is active via Webhook!' });
  }

  try {
    const update = req.body;
    
    // Check if message exists
    if (!update.message || !update.message.text) {
      return res.status(200).json({ ok: true });
    }

    const chatId = update.message.chat.id;
    const text = update.message.text.trim();
    const BOT_TOKEN = process.env.BOT_TOKEN;

    // Check if text is a 6-digit PIN code
    if (/^\d{6}$/.test(text)) {
      // Fetch from Postal API
      const apiRes = await fetch(`https://api.postalpincode.in/pincode/${text}`);
      const rawData = await apiRes.json();

      let replyMessage = "";
      if (rawData && rawData[0] && rawData[0].Status === "Success") {
        const po = rawData[0].PostOffice[0];
        replyMessage = 
          `📍 *Location Found!*\n\n` +
          `🔢 *PIN Code:* \`${text}\`\n` +
          `🏛 *Area:* ${po.Name}\n` +
          `🏙 *District:* ${po.District}\n` +
          `🌄 *State:* ${po.State}\n` +
          `🌍 *Country:* ${po.Country}`;
      } else {
        replyMessage = `❌ No records found for PIN code \`${text}\`.`;
      }

      // Send response back to Telegram
      await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: replyMessage,
          parse_mode: 'Markdown'
        })
      });
    }

    return res.status(200).json({ ok: true });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({ error: error.message });
  }
}
