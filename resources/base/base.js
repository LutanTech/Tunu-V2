window.API_URL= 'https://rizz.tunupublishers.com'
// window.API_URL= 'http://127.0.0.1:5000'



let cart = JSON.parse(localStorage.getItem('cart')) || [];
updateCartUI();





function switchTab(category) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('tab-active'));
    document.getElementById(`tab-${category}`).classList.add('tab-active');
    renderBooks(category);
}

function addToCart(id, category) {
    const book = booksData[category].find(b => b.id === id);

    if (!book) return;

    book.quantity = 1
    const existing = cart.find(b=>b.id==book.id)
    if(existing){
        existing.quantity = existing.quantity + 1
        updateCartUI();

    }  else{

    cart.push(book);
    }

    localStorage.setItem('cart', JSON.stringify(cart));

    updateCartUI();
    openCart();
}

function updateCartUI() {
    const list = document.getElementById('cart-items-list');
    const count = document.getElementById('cart-count');
    const total = document.getElementById('cart-total');
    
    if(count){cart.innerText = cart.length;}
    
    if (cart.length === 0 && list) {
        list.innerHTML = `
            <div style="text-align:center; color:#999; margin-top:50px;">
                <i class="fas fa-shopping-cart fa-4x" style="margin-bottom:20px; opacity:0.3;"></i>
                <p>Your cart is empty</p>
            </div>`;
        total.innerText = 'KES 0';
        return;
    }

    let sum = 0;
    if(list){list.innerHTML = '';}
    cart.forEach((item, index) => {
        sum += item.newPrice;
        console.log(item)
        if(list){
        list.innerHTML += `
            <div class="cart-item">
                <img src="${API_URL}/${item.url}" onerror="this.src='https://i.ibb.co/CKRYPD4p/image.png';" alt="">
                <div style="flex:1">
                    <h5 style="font-size:14px; margin-bottom:4px;">${item.title}</h5>
                    <p style="color:var(--magenta); font-weight:800;">KES ${item.newPrice}</p>
                    <p> <b>Quantity: </b> ${item.quantity} <p>
                </div>
                <button onclick="removeFromCart(${index})" style="background:none; border:none; color:#ff4d4d; cursor:pointer; padding:10px;">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        }
    });
    if(total){
    total.innerText = `KES ${sum}`;
    }
}

function removeFromCart(index) {
    cart.splice(index, 1);

    localStorage.setItem('cart', JSON.stringify(cart));

    updateCartUI();
}

function openCart() {
    document.getElementById('cart-drawer').classList.add('open');
    document.getElementById('overlay').style.display = 'block';
}

function closeCart() {
    document.getElementById('cart-drawer').classList.remove('open');
    document.getElementById('overlay').style.display = 'none';
}
