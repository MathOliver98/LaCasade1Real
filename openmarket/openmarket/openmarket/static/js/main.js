$(document).ready(function () {
    // Toggle advanced search form.
    $("#bt-advanced-search").click(function () {
        // $("#advanced-search-form").toggle();
        $("#advanced-search-form").toggleClass("is-hidden");
        $("#search_keyword").prop("disabled", !$("#search_keyword").prop("disabled"));
        $("#bt-search").prop("disabled", !$("#bt-search").prop("disabled"));
    });

    // Reset advanced search form contents.
    $("#bt-reset-adv-search").click(function () {
        $("#advanced-search-form .input").each(function () {
            this.value = "";
        })
    });

    // Show/hide password.
    $("span.toggle-password").click(function () {
        var field = $(this).siblings("input").eq(0);
        $(this).children("i").eq(0).toggleClass("fa-eye fa-eye-slash");
        if (field.prop("type") == "password") {
            field.prop("type", "text");
        } else {
            field.prop("type", "password");
        }
    });

});

document.addEventListener('DOMContentLoaded', () => {
    // Get all "navbar-burger" elements
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    // Add a click event on each of them
    $navbarBurgers.forEach(el => {
        el.addEventListener('click', () => {

            // Get the target from the "data-target" attribute
            const target = el.dataset.target;
            const $target = document.getElementById(target);

            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            el.classList.toggle('is-active');
            $target.classList.toggle('is-active');

        });
    });

    // Close notifications
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        const $notification = $delete.parentNode;

        $delete.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
        });
    });

    // Product modals
    // const productModal = document.getElementById("modal-product-info");
    // productModal.addEventListener("modal:open", () => {
    //     id = productModal.dataset.id;
    //     getProductData(`products/${id}`).then((data) => {
    //         productModal.querySelector("#product-name").textContent = data.name;
    //         productModal.querySelector("#product-description").textContent = data.description;
    //     });
    // })

    const formDeleteProduct = document.getElementById('modal-delete-product');
    if (formDeleteProduct !== null) {
        formDeleteProduct.addEventListener('submit', (event) => {
            event.preventDefault();
            const productId = formDeleteProduct.dataset.id;
            const endpoint = formDeleteProduct.dataset.next;
            formDeleteProduct.action = `/products/${productId}/delete?next=${endpoint}`;
            formDeleteProduct.submit();
        });
    }


    const formEditProduct = document.getElementById("modal-edit-product");
    if (formEditProduct !== null) {
        formEditProduct.addEventListener("modal:open", () => {
            const productId = formEditProduct.dataset.id;
            getProductData(`/products/${productId}`).then((data) => {
                formEditProduct.querySelector("#name").value = data.name;
                formEditProduct.querySelector("#description").value = data.description;
                formEditProduct.querySelector("#quantity").value = data.quantity;
                formEditProduct.querySelector("#price").value = data.price.toLocaleString(
                    undefined,
                    { minimumFractionDigits: 2 }
                );
            });
        });

        formEditProduct.addEventListener("submit", (event) => {
            event.preventDefault();
            const productId = formEditProduct.dataset.id;
            const endpoint = formEditProduct.dataset.next;
            formEditProduct.action = `/products/${productId}/edit?next=${endpoint}`;
            formEditProduct.submit();
        });
    }

    async function getProductData(url) {
        const response = await fetch(`${url}?` + new URLSearchParams({ json: true }), {
            method: "GET",
            headers: {
                'Content-Type': 'application/json'
            },
        });

        return response.json();
    };

    async function favoriteProduct(id) {
        const response = await fetch(`/products/${id}/favorite`, {
            method: "POST",
        });

        return response.text;
    }

    (document.querySelectorAll('.like') || []).forEach(($like) => {
        const productId = $like.dataset.id;


        $like.addEventListener('click', () => {
            favoriteProduct(productId).then(() => {
                const card = $like.closest(".card");

                // Toggle icon color
                var icon = card.querySelector(".icon-favorite");
                icon.classList.toggle("has-text-danger");

                // Increase count
                var favorites = card.querySelector(".favorites")
                var count = parseInt(favorites.innerText);

                // Toggle button text
                var span = card.querySelector(".favorite-text");
                if (span.innerText == "Favorite") {
                    span.innerHTML = "Unfavorite";
                    favorites.innerHTML = `<i class='fas fa-heart mr-1'></i>\n${count + 1}`;
                } else {
                    span.innerHTML = "Favorite";
                    favorites.innerHTML = `<i class='fas fa-heart mr-1'></i>\n${count - 1}`;
                }
            });
        });
    });
});
