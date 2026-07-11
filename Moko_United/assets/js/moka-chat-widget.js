/* Moka Asistan — chatbot widget (yarım buton + sohbet paneli) */
(function () {
  const CHAT_API_URL = window.MOKA_CHAT_API_URL || "http://localhost:8000/chat";
  const DISPUTE_URL = "https://mokaitiraz.com";

  const style = document.createElement("style");
  style.textContent = `
#yarim{position:fixed;bottom:24px;right:24px;z-index:9998;width:60px;height:60px;border-radius:50%;border:none;cursor:pointer;background:linear-gradient(135deg,#12B39A,#0C8C7E);color:#fff;font-size:26px;display:flex;align-items:center;justify-content:center;box-shadow:0 12px 32px rgba(14,26,43,.24);transition:transform .15s;}
#yarim:hover{transform:translateY(-2px) scale(1.04);}
#yarim.hidden{display:none;}
#yarim .mc-pulse{position:absolute;top:-2px;right:-2px;width:12px;height:12px;border-radius:50%;background:#F0602E;box-shadow:0 0 0 2px #fff;animation:mc-pulse-anim 2s infinite;}
@keyframes mc-pulse-anim{0%{box-shadow:0 0 0 0 rgba(240,96,46,.55);}70%{box-shadow:0 0 0 8px rgba(240,96,46,0);}100%{box-shadow:0 0 0 0 rgba(240,96,46,0);}}

#moka-chat{position:fixed;bottom:24px;right:24px;z-index:9999;width:390px;max-width:calc(100vw - 32px);height:600px;max-height:calc(100vh - 48px);background:#fff;border-radius:20px;box-shadow:0 12px 40px rgba(14,26,43,.14);display:none;flex-direction:column;overflow:hidden;transform:translateY(16px) scale(.97);opacity:0;transition:transform .22s cubic-bezier(.2,.8,.2,1),opacity .22s;font-family:"Inter",system-ui,sans-serif;}
#moka-chat.open{display:flex;transform:translateY(0) scale(1);opacity:1;}
#moka-chat .mc-head{background:linear-gradient(135deg,#12B39A,#0C8C7E);color:#fff;padding:18px 20px;display:flex;align-items:center;gap:12px;}
#moka-chat .mc-avatar{width:38px;height:38px;border-radius:11px;background:rgba(255,255,255,.18);display:grid;place-items:center;font-size:19px;}
#moka-chat .mc-head .t{font-weight:600;font-size:16px;line-height:1.2;}
#moka-chat .mc-head .s{font-size:12px;opacity:.85;display:flex;align-items:center;gap:6px;}
#moka-chat .mc-head .dot{width:7px;height:7px;border-radius:50%;background:#7CF0C4;}
#moka-chat .mc-close{margin-left:auto;background:rgba(255,255,255,.15);border:none;color:#fff;width:32px;height:32px;border-radius:9px;cursor:pointer;font-size:18px;line-height:1;}
#moka-chat .mc-body{flex:1;overflow-y:auto;padding:20px;background:#EEF1F5;display:flex;flex-direction:column;gap:12px;}
#moka-chat .mc-body::-webkit-scrollbar{width:6px;}
#moka-chat .mc-body::-webkit-scrollbar-thumb{background:#CBD5DF;border-radius:3px;}
#moka-chat .bubble{max-width:82%;padding:11px 15px;border-radius:16px;font-size:14px;line-height:1.5;animation:mc-rise .22s ease;white-space:pre-wrap;}
@keyframes mc-rise{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:none;}}
#moka-chat .bubble.bot{background:#fff;border:1px solid #E2E7EE;align-self:flex-start;border-bottom-left-radius:5px;}
#moka-chat .bubble.user{background:#0E1A2B;color:#fff;align-self:flex-end;border-bottom-right-radius:5px;}
#moka-chat .redirect-card{align-self:flex-start;max-width:92%;background:#FFF4EF;border:1px solid #F8C9B5;border-radius:16px;padding:16px;animation:mc-rise .3s ease;}
#moka-chat .redirect-card .rc-title{font-weight:600;font-size:14px;margin-bottom:4px;}
#moka-chat .redirect-card .rc-sub{font-size:13px;color:#5A6B7B;margin-bottom:12px;}
#moka-chat .redirect-card a{display:flex;align-items:center;justify-content:center;gap:8px;background:#F0602E;color:#fff;text-decoration:none;font-weight:600;font-size:14px;padding:12px;border-radius:11px;box-shadow:0 6px 16px rgba(240,96,46,.32);transition:background .15s;}
#moka-chat .redirect-card a:hover{background:#D64E20;}
#moka-chat .typing{align-self:flex-start;background:#fff;border:1px solid #E2E7EE;padding:13px 16px;border-radius:16px;border-bottom-left-radius:5px;display:flex;gap:4px;}
#moka-chat .typing span{width:7px;height:7px;border-radius:50%;background:#B4C0CC;animation:mc-blink 1.3s infinite;}
#moka-chat .typing span:nth-child(2){animation-delay:.2s;}
#moka-chat .typing span:nth-child(3){animation-delay:.4s;}
@keyframes mc-blink{0%,60%,100%{opacity:.3;}30%{opacity:1;}}
#moka-chat .mc-foot{padding:14px 16px;border-top:1px solid #E2E7EE;background:#fff;}
#moka-chat .mc-input{display:flex;gap:8px;align-items:flex-end;background:#EEF1F5;border:1px solid #E2E7EE;border-radius:14px;padding:6px 6px 6px 14px;}
#moka-chat .mc-input textarea{flex:1;border:none;background:none;resize:none;outline:none;font-family:"Inter",system-ui,sans-serif;font-size:14px;line-height:1.4;max-height:96px;padding:6px 0;color:#0E1A2B;}
#moka-chat .mc-send{width:38px;height:38px;border-radius:10px;border:none;cursor:pointer;flex-shrink:0;background:#12B39A;color:#fff;font-size:17px;display:grid;place-items:center;}
#moka-chat .mc-send:disabled{background:#C3D0DA;cursor:not-allowed;}
#moka-chat .mc-hint{font-size:11px;color:#5A6B7B;text-align:center;margin-top:8px;}
#moka-chat .quick{display:flex;flex-wrap:wrap;gap:7px;}
#moka-chat .quick button{background:#fff;border:1px solid #E2E7EE;color:#0C8C7E;font-family:"Inter",system-ui,sans-serif;font-size:12.5px;font-weight:500;padding:7px 12px;border-radius:100px;cursor:pointer;}
#moka-chat .quick button:hover{background:rgba(18,179,154,.08);border-color:#12B39A;}
`;
  document.head.appendChild(style);

  const launcher = document.createElement("button");
  launcher.id = "yarim";
  launcher.setAttribute("aria-label", "Yardım asistanını aç");
  launcher.innerHTML = `<span>💬</span><span class="mc-pulse"></span>`;
  launcher.style.position = "fixed";

  const chat = document.createElement("div");
  chat.id = "moka-chat";
  chat.setAttribute("role", "dialog");
  chat.setAttribute("aria-label", "Moka Asistan");
  chat.innerHTML = `
    <div class="mc-head">
      <div class="mc-avatar">🤖</div>
      <div>
        <div class="t">Moka Asistan</div>
        <div class="s"><span class="dot"></span> Çevrimiçi</div>
      </div>
      <button class="mc-close" id="mc-close" aria-label="Kapat">×</button>
    </div>
    <div class="mc-body" id="mc-body"></div>
    <div class="mc-foot">
      <div class="mc-input">
        <textarea id="mc-text" rows="1" placeholder="Mesajınızı yazın…"></textarea>
        <button class="mc-send" id="mc-send" aria-label="Gönder">➤</button>
      </div>
      <div class="mc-hint">Güvenliğiniz için kart numarası veya şifre paylaşmayın.</div>
    </div>
  `;

  document.addEventListener("DOMContentLoaded", () => {
    document.body.appendChild(launcher);
    document.body.appendChild(chat);

    const body = chat.querySelector("#mc-body");
    const input = chat.querySelector("#mc-text");
    const sendBtn = chat.querySelector("#mc-send");
    const messages = [];
    let busy = false, redirected = false, opened = false;

    launcher.addEventListener("click", openChat);
    chat.querySelector("#mc-close").addEventListener("click", () => {
      chat.classList.remove("open");
      launcher.classList.remove("hidden");
    });
    sendBtn.addEventListener("click", () => send());
    input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
    input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 96) + "px"; });

    function openChat() {
      launcher.classList.add("hidden");
      chat.classList.add("open");
      if (!opened) {
        opened = true;
        addBot("Merhaba! Ben Moka Asistan 👋\nSize nasıl yardımcı olabilirim?");
        addQuick(["Ekstremde tanımadığım işlem var", "Kartımdan çekim yapıldı", "İtiraz etmek istiyorum"]);
      }
      setTimeout(() => input.focus(), 250);
    }
    function addBot(t) { const e = document.createElement("div"); e.className = "bubble bot"; e.textContent = t; body.appendChild(e); scrollBody(); }
    function addUser(t) { const e = document.createElement("div"); e.className = "bubble user"; e.textContent = t; body.appendChild(e); scrollBody(); }
    function addQuick(items) {
      const w = document.createElement("div"); w.className = "quick";
      items.forEach(t => { const b = document.createElement("button"); b.textContent = t; b.onclick = () => { w.remove(); send(t); }; w.appendChild(b); });
      body.appendChild(w); scrollBody();
    }
    function showRedirectCard() {
      const c = document.createElement("div"); c.className = "redirect-card";
      c.innerHTML = `<div class="rc-title">İşleminizi burada çözebilirsiniz</div>
        <div class="rc-sub">İtiraz portalında işleminizi sorgulayın ve gerekirse itirazınızı başlatın.</div>
        <a href="${DISPUTE_URL}" target="_blank" rel="noopener">İtiraz Portalına Git →</a>`;
      body.appendChild(c); scrollBody();
    }
    function typingOn() { const t = document.createElement("div"); t.className = "typing"; t.id = "mc-typing"; t.innerHTML = "<span></span><span></span><span></span>"; body.appendChild(t); scrollBody(); }
    function typingOff() { chat.querySelector("#mc-typing")?.remove(); }
    function scrollBody() { body.scrollTop = body.scrollHeight; }

    async function callBackend() {
      const res = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages })
      });
      if (!res.ok) throw new Error("API " + res.status);
      return await res.json();
    }

    async function send(preset) {
      const text = (preset ?? input.value).trim();
      if (!text || busy) return;
      input.value = ""; input.style.height = "auto";
      addUser(text);
      messages.push({ role: "user", content: text });
      busy = true; sendBtn.disabled = true; typingOn();
      try {
        const { reply, redirect } = await callBackend();
        typingOff();
        if (reply) addBot(reply);
        if (redirect && !redirected) { redirected = true; showRedirectCard(); }
        messages.push({ role: "assistant", content: reply });
      } catch (err) {
        typingOff(); console.error(err);
        addBot("Şu an bir bağlantı sorunu yaşıyorum. Lütfen birazdan tekrar deneyin.");
      } finally {
        busy = false; sendBtn.disabled = false; input.focus();
      }
    }
  });
})();
