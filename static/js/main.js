function loadBoxes(storageId) {
    $.ajax({
        url: `/get_boxes/${storageId}/`,
        method: "GET",
        success: function (response) {
            generatedBoxes(response.boxes)
        },
        error: function (xhr, status, error) {
            console.error("Ошибка загрузки данных:", error);
        }
    });
}


function generatedBoxes(boxes) {
    const allTab = document.querySelector("#pills-all");
    const to3Tab = document.querySelector("#pills-to3");
    const to10Tab = document.querySelector("#pills-to10");
    const from10Tab = document.querySelector("#pills-from10");

    allTab.innerHTML = '';
    to3Tab.innerHTML = '';
    to10Tab.innerHTML = '';
    from10Tab.innerHTML = '';

    addBoxesToTab(allTab, boxes);
    addBoxesToTab(to3Tab, boxes.filter(box => box.area <= 3));
    addBoxesToTab(to10Tab, boxes.filter(box => box.area > 3 && box.area <= 10));
    addBoxesToTab(from10Tab, boxes.filter(box => box.area > 10));
}

// Функция для добавления боксов в раздел с возможностью скрытия
function addBoxesToTab(tab, boxes) {
    // Добавить первые два бокса
    boxes.slice(0, 2).forEach((box) => {
        const boxElement = createBoxElement(box);
        tab.appendChild(boxElement);
    });

    // Если боксов больше двух, скрыть остальные
    if (boxes.length > 2) {
        const hiddenBoxContainer = document.createElement('div');
        hiddenBoxContainer.className = 'collapse';
        hiddenBoxContainer.id = 'collapse-all';

        // Добавить остальные боксы в скрытый контейнер
        boxes.slice(2).forEach((box) => {
            const boxElement = createBoxElement(box);
            hiddenBoxContainer.appendChild(boxElement);
        });

        // Кнопка для раскрытия скрытых боксов
        const collapseButton = document.createElement('button');
        collapseButton.className = 'btn w-auto py-3 px-5 SelfStorage__bg_orange SelfStorage__btn2_orange text-white text-center fs_24 border-8';
        collapseButton.id = 'btn-collapse-all';
        collapseButton.setAttribute('data-bs-toggle', 'collapse');
        collapseButton.setAttribute('data-bs-target', '#collapse-all');
        collapseButton.setAttribute('aria-expanded', 'false');
        collapseButton.setAttribute('aria-controls', 'collapse-all');
        collapseButton.innerText = 'Другие боксы';
        collapseButton.addEventListener('click', () => {
            collapseButton.classList.add('d-none');
        });

        tab.appendChild(collapseButton);
        tab.appendChild(hiddenBoxContainer);
    }
}

// Функция для создания элемента бокса
function createBoxElement(box) {
    const boxElement = document.createElement('a');
    boxElement.href = '#';
    boxElement.className = 'row text-decoration-none py-3 px-4 mt-5 SelfStorage__boxlink';
    boxElement.innerHTML = `
            <div class="col-12 col-md-4 col-lg-3 d-flex justify-content-center align-items-center">
                <span class="SelfStorage_green fs_24 me-2">${box.level} эт.</span><span class="fs_24">${box.number}</span>
            </div>
            <div class="col-6 col-md-4 col-lg-3 d-flex justify-content-center align-items-center">
                <span class="fs_24">${box.area} м²</span>
            </div>
            <div class="col-6 col-md-4 col-lg-3 d-flex justify-content-center align-items-center">
                <span class="fs_24">${box.width} x ${box.length} x ${box.height}</span>
            </div>
            <div class="col-12 col-lg-3">
                <span class="btn my-2 w-100 text-white fs_24 SelfStorage__bg_orange SelfStorage__btn2_orange border-8">От ${box.price} ₽</span>
            </div>
        `;
    return boxElement;
}
