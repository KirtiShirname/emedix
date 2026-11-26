const express = require("express");
const qrcode = require("qrcode-terminal");
const { Client, LocalAuth } = require("whatsapp-web.js");

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./session" }),
  puppeteer: { args: ["--no-sandbox"] },
});
let ready = false;

client.on("qr", (qr) => { console.log("Scan this QR with the business WhatsApp:"); qrcode.generate(qr, { small: true }); });
client.on("ready", () => { ready = true; console.log("WhatsApp ready as", client.info.wid.user); });
client.on("disconnected", () => { ready = false; console.log("Disconnected"); });
client.initialize();

const app = express();
app.use(express.json());

app.post("/send-group", async (req, res) => {
  try {
    if (!ready) return res.status(503).send("WhatsApp not ready");
    const { group, text, expectedSender } = req.body;
    const me = client.info.wid.user;
    if (expectedSender && !me.endsWith(expectedSender.replace(/\D/g, "")))
      return res.status(409).send(`Logged-in number ${me} != SENDER_NUMBER ${expectedSender}`);
    const chats = await client.getChats();
    const g = chats.find((c) => c.isGroup && c.name.toLowerCase() === group.toLowerCase());
    if (!g) return res.status(404).send(`Group '${group}' not found. Is the number added to it?`);
    await g.sendMessage(text);
    res.send("ok");
  } catch (e) { res.status(500).send(String(e)); }
});

app.post("/send-direct", async (req, res) => {
  try {
    if (!ready) return res.status(503).send("WhatsApp not ready");
    let n = req.body.phone.replace(/\D/g, "");
    if (n.length === 10) n = "91" + n;
    const id = await client.getNumberId(n);
    if (!id) return res.status(404).send("Number not on WhatsApp");
    await client.sendMessage(id._serialized, req.body.text);
    res.send("ok");
  } catch (e) { res.status(500).send(String(e)); }
});

app.listen(3000, "127.0.0.1", () => console.log("WA service on :3000"));
