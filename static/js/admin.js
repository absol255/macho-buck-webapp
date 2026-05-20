async function createUser() {
    const username = document.getElementById("create-username").value;

    const response = await fetch("/api/admin/create-user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username
        })
    });

    const data = await response.json();

    alert(JSON.stringify(data, null, 2));
}

async function addBucks() {
    const username = document.getElementById("bucks-username").value;
    const amount = document.getElementById("bucks-amount").value;

    const response = await fetch("/api/admin/add-bucks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username,
            amount
        })
    });

    const data = await response.json();

    alert(JSON.stringify(data, null, 2));
}

async function setBucks() {
    const username = document.getElementById("set-username").value;
    const amount = document.getElementById("set-amount").value;

    const response = await fetch("/api/admin/set-bucks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username,
            amount
        })
    });

    const data = await response.json();

    alert(JSON.stringify(data, null, 2));
}

async function deleteUser() {

    const username =
        document.getElementById(
            "delete-username"
        ).value

    const confirmed = confirm(
        `Delete ${username}?`
    )

    if (!confirmed) {
        return
    }

    const response = await fetch(
        "/api/admin/delete-user",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username
            })
        }
    )

    const data = await response.json()

    alert(
        JSON.stringify(data, null, 2)
    )
}

function logout() {
    window.location = "/logout";
}