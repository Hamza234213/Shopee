/* ---------- State ---------- */
let token = localStorage.getItem("token");
let currentUser = null;
let currentCategory = "All";

const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({
  "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
}[c]));

/* ---------- API helper ---------- */
async function api(url, opt = {}){
  opt.headers = { ...(opt.headers || {}), ...(token ? { Authorization: "Bearer " + token } : {}) };
  if (opt.body && typeof opt.body !== "string"){
    opt.headers["Content-Type"] = "application/json";
    opt.body = JSON.stringify(opt.body);
  }
  const r = await fetch(url, opt);
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || "Request failed");
  return d;
}

/* ---------- Products ---------- */
async function loadProducts(){
  let q = new URLSearchParams();
  if (currentCategory !== "All") q.set("category", currentCategory);
  let data = await api("/api/products?" + q);

  $("#products").innerHTML = data.length
    ? data.map(p => `
      <article class="product">
        ${p.old_price ? `<span class="tag">Em promoção</span>` : ""}
        <img src="${p.image}" alt="">
        <h3>${esc(p.name)}</h3>
        <p class="desc">${esc(p.description || "")}</p>
        <div class="price-row">
          <span class="price">R$${Number(p.price).toFixed(2)}</span>
          ${p.old_price ? `<span class="old-price">R$${Number(p.old_price).toFixed(2)}</span>` : ""}
        </div>
        <button class="add" onclick="addCart('${p._id}')">Adicionar</button>
      </article>
    `).join("")
    : "<p class='muted-box'>No products found.</p>";
}

/* ---------- Categories (HTML buttons) ---------- */
function setCat(cat){
  currentCategory = (currentCategory === cat) ? "All" : cat;
  document.querySelectorAll(".cat").forEach(b => {
    b.classList.toggle("active", b.dataset.cat === currentCategory);
  });
  loadProducts();
}

/* ---------- Cart ---------- */
async function addCart(id){
  if (!token) return loginModal();
  try {
    await api("/api/cart", { method: "POST", body: { product_id: id } });
    alert("Added to cart");
    updateCartCount();
  } catch (e) { alert(e.message); }
}

async function updateCartCount(){
  if (!token){ $("#cartCount").textContent = "0"; return; }
  try {
    const items = await api("/api/cart");
    $("#cartCount").textContent = items.reduce((a, x) => a + x.quantity, 0);
  } catch {}
}

async function showCart(){
  if (!token) return loginModal();
  const items = await api("/api/cart");
  $("#modalContent").innerHTML = `
    <h2 id="modalTitle">Your Cart</h2>
    ${items.length
      ? items.map(x => `
          <div class="cart-row">
            <img src="${x.product.image}" alt="">
            <div>
              <b>${esc(x.product.name)}</b>
              <div class="meta">R$${Number(x.product.price).toFixed(2)} × ${x.quantity}</div>
            </div>
            <button class="add" style="width:auto;padding:6px 10px" onclick="removeCart('${x._id}')">×</button>
          </div>
        `).join("") +
        `<button class="primary" style="margin-top:18px;width:100%" onclick="checkout()">Checkout</button>`
      : "<p class='muted-box'>Your cart is empty.</p>"}`;
  openModal();
}

async function removeCart(id){
  await api("/api/cart/" + id, { method: "DELETE" });
  showCart();
  updateCartCount();
}

async function checkout(){
  const address = prompt("Delivery address:");
  if (!address) return;
  try {
    await api("/api/orders", { method: "POST", body: { address } });
    closeModal();
    alert("Order placed successfully");
    updateCartCount();
    loadOrders();
  } catch (e) { alert(e.message); }
}

/* ---------- Auth ---------- */
function loginModal(){
  openModal();
  $("#modalContent").innerHTML = `
    <h2 id="modalTitle">Welcome back</h2>
    <form class="form" onsubmit="login(event)">
      <input id="email" type="email" placeholder="Email" required>
      <input id="password" type="password" placeholder="Password" required>
      <button class="primary" style="width:100%">Login</button>
    </form>
    <p class="meta">Demo: demo@shopverse.local / Demo@12345</p>
    <button class="add" onclick="registerModal()">Create account</button>`;
}

function registerModal(){
  openModal();
  $("#modalContent").innerHTML = `
    <h2 id="modalTitle">Create account</h2>
    <form class="form" onsubmit="register(event)">
      <input id="name" placeholder="Full name" required>
      <input id="email" type="email" placeholder="Email" required>
      <input id="password" type="password" placeholder="Password" required>
      <button class="primary" style="width:100%">Register</button>
    </form>`;
}

async function login(e){
  e.preventDefault();
  try {
    const d = await api("/api/auth/login", { method: "POST", body: {
      email: $("#email").value, password: $("#password").value
    }});
    token = d.token;
    localStorage.setItem("token", token);
    closeModal();
    $("#loginBtn").textContent = "Account";
    updateCartCount(); loadOrders(); loadWallet();
  } catch (x) { alert(x.message); }
}

async function register(e){
  e.preventDefault();
  try {
    const d = await api("/api/auth/register", { method: "POST", body: {
      name: $("#name").value, email: $("#email").value, password: $("#password").value
    }});
    token = d.token;
    localStorage.setItem("token", token);
    closeModal();
    $("#loginBtn").textContent = "Account";
    updateCartCount(); loadOrders(); loadWallet();
  } catch (x) { alert(x.message); }
}

function logout(){
  token = null;
  localStorage.removeItem("token");
  currentUser = null;
  $("#loginBtn").textContent = "Login";
  $("#cartCount").textContent = "0";
  $("#ordersList").textContent = "Login to view your orders.";
  $("#walletBox").textContent = "Login to view wallet.";
}

/* ---------- Orders ---------- */
async function loadOrders(){
  if (!token) return;
  try {
    const d = await api("/api/orders");
    $("#ordersList").innerHTML = d.length
      ? d.map(o => `
          <div class="cart-row">
            <div>
              <b>Order #${o._id.slice(-6)}</b>
              <div class="meta">${esc(o.status)} · ${new Date(o.created_at).toLocaleString()}</div>
            </div>
            <strong>R$${Number(o.total).toFixed(2)}</strong>
          </div>
        `).join("")
      : "<p class='muted-box'>No orders yet.</p>";
  } catch {}
}

/* ---------- Wallet ---------- */
async function loadWallet(){
  if (!token) return;
  try {
    const p = await api("/api/profile");
    $("#walletBox").innerHTML = `
      <div class="muted-box" style="padding:20px">
        <div class="meta">AVAILABLE BALANCE</div>
        <div style="font-size:28px;font-weight:800;margin:6px 0 14px">R$${Number(p.wallet).toFixed(2)}</div>
        <button class="primary" onclick="walletAction('deposit')">Deposit</button>
        <button class="add" style="width:auto" onclick="walletAction('withdraw')">Withdraw</button>
      </div>`;
  } catch {}
}

async function walletAction(type){
  const amount = prompt("Enter amount");
  if (!amount) return;
  try {
    await api("/api/wallet/" + type, { method: "POST", body: { amount: Number(amount) } });
    loadWallet();
    alert("Demo wallet transaction completed");
  } catch (e) { alert(e.message); }
}

/* ---------- Modal helpers ---------- */
function openModal(){ $("#modal").classList.remove("hidden"); }
function closeModal(){ $("#modal").classList.add("hidden"); }

/* ---------- Search ---------- */
function searchPrompt(){
  const q = prompt("Search product");
  if (!q) return;
  location.hash = "#shop";
  api("/api/products?q=" + encodeURIComponent(q)).then(data => {
    $("#products").innerHTML = data.length
      ? data.map(p => `
          <article class="product">
            ${p.old_price ? `<span class="tag">Em promoção</span>` : ""}
            <img src="${p.image}" alt="">
            <h3>${esc(p.name)}</h3>
            <p class="desc">${esc(p.description || "")}</p>
            <div class="price-row">
              <span class="price">R$${Number(p.price).toFixed(2)}</span>
              ${p.old_price ? `<span class="old-price">R$${Number(p.old_price).toFixed(2)}</span>` : ""}
            </div>
            <button class="add" onclick="addCart('${p._id}')">Adicionar</button>
          </article>
        `).join("")
      : "<p class='muted-box'>No products found.</p>";
  });
}

/* ---------- Language dropdown ---------- */
function initLang(){
  const btn  = $("#langBtn");
  const menu = $("#langMenu");
  const label= $("#langLabel");
  if (!btn || !menu) return;
  btn.addEventListener("click", e => { e.stopPropagation(); menu.classList.toggle("hidden"); });
  menu.addEventListener("click", e => {
    const b = e.target.closest("button[data-lang]");
    if (!b) return;
    label.textContent = b.dataset.lang;
    menu.classList.add("hidden");
  });
  document.addEventListener("click", () => menu.classList.add("hidden"));
}

/* ---------- Init ---------- */
function init(){
  // Category buttons
  document.querySelectorAll(".cat").forEach(b => {
    b.addEventListener("click", () => setCat(b.dataset.cat));
  });

  $("#cartBtn").onclick   = showCart;
  $("#searchBtn").onclick = searchPrompt;
  $("#loginBtn").onclick  = () => token ? location.hash = "#wallet" : loginModal();

  // Click backdrop to close modal
  $("#modal").addEventListener("click", e => { if (e.target.id === "modal") closeModal(); });

  initLang();

  loadProducts();
  if (token){ updateCartCount(); loadOrders(); loadWallet(); }
}

document.addEventListener("DOMContentLoaded", init);