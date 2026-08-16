import Sortable from "sortablejs";

const dragItemSelector = "[data-drag-item]";
const dragListSelector = "[data-drag-list]";
const dragHandleSelector = "[data-drag-handle]";
const sortableInstances = new WeakMap();
const dragStates = new WeakMap();
const reorderVersions = new WeakMap();

let liveRegion = null;

function getDragItems(list) {
  return Array.from(list.children).filter((child) =>
    child.matches(dragItemSelector),
  );
}

function getOrder(list) {
  return getDragItems(list).map((item) => item.dataset.dragId);
}

function applyOrder(list, order) {
  const itemsById = new Map(
    getDragItems(list).map((item) => [String(item.dataset.dragId), item]),
  );
  const orderedItems = [];

  order.forEach((id) => {
    const item = itemsById.get(id);
    if (item) orderedItems.push(item);
    itemsById.delete(id);
  });
  orderedItems.push(...itemsById.values());

  orderedItems.forEach((item) => list.appendChild(item));
}

function announce(message) {
  if (!liveRegion) {
    liveRegion = document.createElement("div");
    liveRegion.className = "sr-only";
    liveRegion.setAttribute("role", "status");
    liveRegion.setAttribute("aria-live", "polite");
    document.body.appendChild(liveRegion);
  }
  liveRegion.textContent = "";
  window.requestAnimationFrame(() => {
    if (liveRegion) liveRegion.textContent = message;
  });
}

function getCsrfToken() {
  const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (input?.value) return input.value;

  const cookie = document.cookie
    .split("; ")
    .find((value) => value.startsWith("csrftoken="));
  return cookie ? decodeURIComponent(cookie.slice("csrftoken=".length)) : "";
}

async function persistOrder(list, order, previousOrder) {
  const url = list.dataset.dragReorderUrl;
  if (!url) return;

  const version = (reorderVersions.get(list) || 0) + 1;
  reorderVersions.set(list, version);

  try {
    const response = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ order }),
    });
    if (!response.ok) throw new Error("The order could not be saved.");
    if (reorderVersions.get(list) === version) announce("Order saved.");
  } catch {
    if (reorderVersions.get(list) !== version) return;
    applyOrder(list, previousOrder);
    announce("The order could not be saved. Try again.");
  }
}

function createSortable(list) {
  if (sortableInstances.has(list)) return;

  const sortable = new Sortable(list, {
    animation: 150,
    chosenClass: "is-drag-chosen",
    dataIdAttr: "data-drag-id",
    dragClass: "is-dragging",
    draggable: dragItemSelector,
    fallbackOnBody: true,
    ghostClass: "is-drag-ghost",
    handle: dragHandleSelector,
    onStart({ from, item }) {
      dragStates.set(item, { order: getOrder(from) });
      from.classList.add("is-drag-over");
      item.setAttribute("aria-grabbed", "true");
    },
    onEnd({ from, item, to, oldIndex, newIndex }) {
      from.classList.remove("is-drag-over");
      to.classList.remove("is-drag-over");
      item.setAttribute("aria-grabbed", "false");

      if (oldIndex !== newIndex) {
        announce(`Moved ${item.dataset.dragLabel || "item"}.`);
        persistOrder(to, getOrder(to), dragStates.get(item)?.order || []);
      }
      dragStates.delete(item);
    },
  });

  sortableInstances.set(list, sortable);
}

function moveItemWithKeyboard(item, direction) {
  const list = item.closest(dragListSelector);
  if (!list) return;

  const items = getDragItems(list);
  const currentIndex = items.indexOf(item);
  const nextIndex = currentIndex + direction;
  if (nextIndex < 0 || nextIndex >= items.length) return;
  const previousOrder = getOrder(list);

  const nextItem = items[nextIndex];
  if (direction < 0) {
    list.insertBefore(item, nextItem);
  } else if (nextItem.nextElementSibling) {
    list.insertBefore(item, nextItem.nextElementSibling);
  } else {
    list.appendChild(item);
  }

  sortableInstances.get(list)?.sort(
    getDragItems(list).map((candidate) => candidate.dataset.dragId),
    true,
  );
  item.querySelector(dragHandleSelector)?.focus();
  announce(
    `Moved ${item.dataset.dragLabel || "item"} ${direction < 0 ? "up" : "down"}.`,
  );
  persistOrder(list, getOrder(list), previousOrder);
}

function handleKeyboardReorder(event) {
  const handle =
    event.target instanceof Element
      ? event.target.closest(dragHandleSelector)
      : null;
  if (!handle) return;

  const item = handle.closest(dragItemSelector);
  if (!item) return;

  if (event.key === "ArrowUp" || event.key === "ArrowDown") {
    event.preventDefault();
    event.stopPropagation();
    moveItemWithKeyboard(item, event.key === "ArrowUp" ? -1 : 1);
    return;
  }

  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    event.stopPropagation();
    announce(
      `Use the up and down arrow keys to move ${item.dataset.dragLabel || "item"}.`,
    );
  }
}

function initializeDragLists() {
  document.querySelectorAll(dragListSelector).forEach((list) => {
    createSortable(list);
  });
}

document.addEventListener("keydown", handleKeyboardReorder, true);
document.addEventListener("htmx:afterSwap", initializeDragLists);

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeDragLists, { once: true });
} else {
  initializeDragLists();
}
