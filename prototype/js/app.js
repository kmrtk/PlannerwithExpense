// カレンダー画面：予定モーダルの開閉と仮の追加・編集・削除
(function () {
  var modal = document.getElementById('schedule-modal');
  if (!modal) return;

  var titleEl = document.getElementById('schedule-modal-title');
  var form = document.getElementById('schedule-form');
  var titleInput = document.getElementById('schedule-title');
  var dateInput = document.getElementById('schedule-date');
  var memoInput = document.getElementById('schedule-memo');
  var deleteBtn = document.getElementById('schedule-delete');
  var cancelBtn = document.getElementById('schedule-cancel');
  var addBtn = document.getElementById('open-add-schedule');
  var currentChip = null;

  function openModal(mode, chip) {
    currentChip = chip || null;
    if (mode === 'edit' && chip) {
      titleEl.textContent = '予定を編集';
      titleInput.value = chip.dataset.title;
      dateInput.value = chip.dataset.date;
      memoInput.value = chip.dataset.memo;
      deleteBtn.style.display = 'inline-block';
    } else {
      titleEl.textContent = '予定を追加';
      titleInput.value = '';
      dateInput.value = '';
      memoInput.value = '';
      deleteBtn.style.display = 'none';
    }
    modal.classList.add('open');
  }

  function closeModal() {
    modal.classList.remove('open');
    currentChip = null;
  }

  addBtn.addEventListener('click', function () {
    openModal('add');
  });

  document.querySelectorAll('.schedule-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      openModal('edit', chip);
    });
  });

  cancelBtn.addEventListener('click', closeModal);

  deleteBtn.addEventListener('click', function () {
    if (currentChip) {
      currentChip.remove();
    }
    closeModal();
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (currentChip) {
      currentChip.dataset.title = titleInput.value;
      currentChip.dataset.date = dateInput.value;
      currentChip.dataset.memo = memoInput.value;
      currentChip.textContent = titleInput.value;
    } else {
      var chip = document.createElement('span');
      chip.className = 'schedule-chip';
      chip.dataset.title = titleInput.value;
      chip.dataset.date = dateInput.value;
      chip.dataset.memo = memoInput.value;
      chip.textContent = titleInput.value;
      chip.addEventListener('click', function () {
        openModal('edit', chip);
      });
      var cells = document.querySelectorAll('#calendar-body td');
      var target = cells[Math.floor(Math.random() * cells.length)];
      target.appendChild(chip);
    }
    closeModal();
  });
})();

// 家計簿画面：支出モーダルの開閉と仮の追加・編集・削除
(function () {
  var modal = document.getElementById('expense-modal');
  if (!modal) return;

  var titleEl = document.getElementById('expense-modal-title');
  var form = document.getElementById('expense-form');
  var amountInput = document.getElementById('expense-amount');
  var dateInput = document.getElementById('expense-date');
  var categoryInput = document.getElementById('expense-category');
  var memoInput = document.getElementById('expense-memo');
  var deleteBtn = document.getElementById('expense-delete-btn');
  var cancelBtn = document.getElementById('expense-cancel');
  var addBtn = document.getElementById('open-add-expense');
  var tbody = document.getElementById('expense-body');
  var currentRow = null;

  function openModal(mode, row) {
    currentRow = row || null;
    if (mode === 'edit' && row) {
      titleEl.textContent = '支出を編集';
      amountInput.value = row.dataset.amount;
      dateInput.value = row.dataset.date;
      categoryInput.value = row.dataset.category;
      memoInput.value = row.dataset.memo;
      deleteBtn.style.display = 'inline-block';
    } else {
      titleEl.textContent = '支出を追加';
      amountInput.value = '';
      dateInput.value = '';
      categoryInput.value = '';
      memoInput.value = '';
      deleteBtn.style.display = 'none';
    }
    modal.classList.add('open');
  }

  function closeModal() {
    modal.classList.remove('open');
    currentRow = null;
  }

  function bindRowButtons(row) {
    row.querySelector('.expense-edit').addEventListener('click', function () {
      openModal('edit', row);
    });
    row.querySelector('.expense-delete').addEventListener('click', function () {
      row.remove();
    });
  }

  document.querySelectorAll('#expense-body tr').forEach(bindRowButtons);

  addBtn.addEventListener('click', function () {
    openModal('add');
  });

  cancelBtn.addEventListener('click', closeModal);

  deleteBtn.addEventListener('click', function () {
    if (currentRow) {
      currentRow.remove();
    }
    closeModal();
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var amountText = Number(amountInput.value).toLocaleString() + '円';
    if (currentRow) {
      currentRow.dataset.amount = amountInput.value;
      currentRow.dataset.date = dateInput.value;
      currentRow.dataset.category = categoryInput.value;
      currentRow.dataset.memo = memoInput.value;
      var cells = currentRow.querySelectorAll('td');
      cells[0].textContent = dateInput.value;
      cells[1].textContent = categoryInput.value;
      cells[2].textContent = amountText;
      cells[3].textContent = memoInput.value;
    } else {
      var row = document.createElement('tr');
      row.dataset.amount = amountInput.value;
      row.dataset.date = dateInput.value;
      row.dataset.category = categoryInput.value;
      row.dataset.memo = memoInput.value;
      row.innerHTML =
        '<td>' + dateInput.value + '</td>' +
        '<td>' + categoryInput.value + '</td>' +
        '<td>' + amountText + '</td>' +
        '<td>' + memoInput.value + '</td>' +
        '<td><button class="secondary expense-edit">編集</button> <button class="secondary expense-delete">削除</button></td>';
      tbody.appendChild(row);
      bindRowButtons(row);
    }
    closeModal();
  });
})();
