document.addEventListener('DOMContentLoaded', () => {
    // Functions to open and close a modal
    function openModal($el, id, next) {
        // Save product ID in modal.
        $el.dataset.id = id;
        $el.dataset.next = next;

        // Create a custom 'onshow' event.
        var event = new Event('modal:open')
        $el.dispatchEvent(event);

        // Open modal.
        $el.classList.add('is-active');
    }

    function closeModal($el) {
        // Create a custom 'onclose' event.
        var event = new Event('modal:close')
        $el.dispatchEvent(event);

        // Close modal.
        $el.classList.remove('is-active');
    }

    function closeAllModals() {
        (document.querySelectorAll('.modal') || []).forEach(($modal) => {
            closeModal($modal);
        });
    }

    // Add a click event on buttons to open modals
    (document.querySelectorAll('.modal-trigger') || []).forEach(($trigger) => {
        const modal = $trigger.dataset.target;
        const $target = document.getElementById(modal);

        $trigger.addEventListener('click', () => {
            openModal($target, $trigger.dataset.id, $trigger.dataset.next);
        });
    });

    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .close-modal, .delete') || []).forEach(($close) => {
        const $target = $close.closest('.modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
        const e = event || window.event;

        if (e.keyCode === 27) { // Escape key
            const active = document.activeElement;
            const tag = active.tagName.toLowerCase();

            if (tag == "input" || tag == "textarea" || tag == "select") {
                active.blur();
            } else {
                closeAllModals();
            }

        }
    });
});
