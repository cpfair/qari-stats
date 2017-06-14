// https://stackoverflow.com/a/22119674/252309
function findAncestor(el, cls) {
    while ((el = el.parentElement) && !el.classList.contains(cls));
    return el;
}

function resort_items(header_el, key, e) {
    // Use CSS classes to store sort state.
    // Wheee.
    var icon_el = header_el.getElementsByClassName("sort-icon")[0];
    var sort_desc = icon_el.classList.contains("fa-sort-asc");

    // Resort DOM elements according to qari_metadata dict baked into HTML.
    var list = document.getElementById("qari-list");
    var items = list.getElementsByClassName("item");
    Array.prototype.slice.call(items).sort(function(a, b) {
        return (sort_desc ? -1 : 1) * (qari_stats[a.getAttribute("qari")][key] - qari_stats[b.getAttribute("qari")][key]);
    }).forEach(function(item) {
        list.appendChild(item);
    });

    // Update icons.
    Array.prototype.slice.call(document.getElementsByClassName("sort-icon")).forEach(function(other_icon_el) {
        other_icon_el.classList.remove("fa-sort-desc", "fa-sort-asc", "fa-sort");
        other_icon_el.classList.add("fa-sort");
    });
    icon_el.classList.remove("fa-sort");
    icon_el.classList.add(sort_desc ? "fa-sort-desc" : "fa-sort-asc");
}

var current_player_item, current_player_button, current_player_audio;
function play_pause(button_el, e) {
    e.preventDefault();

    // Stop other player, if any.
    if (current_player_audio) {
        current_player_audio.pause();
        current_player_button.classList.remove("fa-stop-circle");
        current_player_button.classList.add("fa-play-circle");
        current_player_item.classList.remove("active");
    }

    if (current_player_button == button_el) {
        // Stop entirely if they're toggling the button.
        current_player_item = current_player_audio = current_player_button = null;
        return;
    }
    // ...otherwise, start playing the new clip.

    // Set up control state.
    current_player_item = findAncestor(button_el, "item");
    current_player_item.classList.add("active");
    current_player_button = button_el;
    current_player_button.classList.add("fa-stop-circle");
    current_player_button.classList.remove("fa-play-circle");
    // Start new audio - button is a link to the mp3.
    current_player_audio = new Audio(button_el.getAttribute("href"));
    current_player_audio.play();
    return false;
}

document.addEventListener("DOMContentLoaded", function() {
    function setup_sort(header_el, key) {
        header_el.addEventListener("click", resort_items.bind(null, header_el, key));
    }
    setup_sort(document.getElementById("sort-speed"), "speed");
    setup_sort(document.getElementById("sort-register"), "register");

    function setup_player(button_el) {
        button_el.addEventListener("click", play_pause.bind(null, button_el));
    }
    Array.prototype.slice.call(document.getElementsByClassName("audio-player")).forEach(setup_player);
});
