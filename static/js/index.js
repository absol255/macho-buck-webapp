const socket = io();

async function loadUsers() {
    const response = await fetch("/api/users");
    const users = await response.json();

    renderUsers(users);
}

function renderUsers(users) {
    const list = document.getElementById("user-list");

    list.innerHTML = "";

    users.forEach(user => {
        const div = document.createElement("div");

        div.className = "user";

        div.innerHTML = `
            <span>${user.username}</span>
            <span class="balance">${user.macho_bucks} M$</span>
        `;

        list.appendChild(div);
    });
}

socket.on("balance_update", () => {
    loadUsers();
});

socket.on("user_created", () => {
    loadUsers();
});

socket.on("user_deleted", () => {
    loadUsers();
});

loadUsers();
