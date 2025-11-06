
let selectedFiles = [];
let existingImages = [];

function initExistingImages(images) {
  existingImages = images.map(img => ({ ...img, keep: true }));
  updatePreview();
}

function previewImages(event) {
  const newFiles = Array.from(event.target.files);
  const limitMsg = document.getElementById('image-limit-msg');

  if (existingImages.filter(img => img.keep).length + selectedFiles.length + newFiles.length > 3) {
    limitMsg.style.display = "block";
  } else {
    limitMsg.style.display = "none";
  }

  selectedFiles = [...selectedFiles, ...newFiles].slice(0, 3 - existingImages.filter(img => img.keep).length);
  updatePreview();
  updateFileInput();
}

function updatePreview() {
  const previewContainer = document.getElementById('preview-container');
  previewContainer.innerHTML = '';

  existingImages.forEach((img, index) => {
    if (!img.keep) return;

    const col = document.createElement('div');
    col.className = 'col-6 col-md-4 p-1';
    col.style.maxWidth = '20rem';

    const wrapper = document.createElement('div');
    wrapper.className = 'position-relative d-inline-block';
    wrapper.style.width = '100%';

    const image = document.createElement('img');
    image.src = img.path;
    image.className = 'img-fluid neon-border';
    image.style.width = '100%';
    image.style.height = 'auto';

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.innerHTML = '<span class="icon"></span>';
    removeBtn.className = 'btn btn-custom position-absolute';
    removeBtn.style.backgroundColor = '#111111';
    removeBtn.style.fontSize = '0.6rem';
    removeBtn.style.lineHeight = '0.5rem';
    removeBtn.style.padding = '0';
    removeBtn.style.width = '1rem';
    removeBtn.style.height = '1rem';
    removeBtn.style.top = '-1px';
    removeBtn.style.right = '-1px';
    removeBtn.style.zIndex = '10';
    removeBtn.onclick = () => {
      img.keep = false;
      updatePreview();
      updateFileInput();
      document.getElementById('image-limit-msg').textContent = "";
    };

    wrapper.appendChild(image);
    wrapper.appendChild(removeBtn);
    col.appendChild(wrapper);
    previewContainer.appendChild(col);
  });

  selectedFiles.forEach((file, index) => {
    const reader = new FileReader();
    reader.onload = function(e) {
      const col = document.createElement('div');
      col.className = 'col-6 col-md-4 p-1';
      col.style.maxWidth = '20rem';

      const wrapper = document.createElement('div');
      wrapper.className = 'position-relative d-inline-block';
      wrapper.style.width = '100%';

      const img = document.createElement('img');
      img.src = e.target.result;
      img.className = 'img-fluid neon-border';
      img.style.width = '100%';
      img.style.height = 'auto';

      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.innerHTML = '<span class="icon"></span>';
      removeBtn.className = 'btn btn-custom position-absolute';
      removeBtn.style.backgroundColor = '#111111';
      removeBtn.style.fontSize = '0.6rem';
      removeBtn.style.lineHeight = '0.5rem';
      removeBtn.style.padding = '0';
      removeBtn.style.width = '1rem';
      removeBtn.style.height = '1rem';
      removeBtn.style.top = '-1px';
      removeBtn.style.right = '-1px';
      removeBtn.style.zIndex = '10';
      removeBtn.onclick = () => {
        selectedFiles.splice(index, 1);
        updatePreview();
        updateFileInput();
        document.getElementById('image-limit-msg').textContent = "";
      };

      wrapper.appendChild(img);
      wrapper.appendChild(removeBtn);
      col.appendChild(wrapper);
      previewContainer.appendChild(col);
    };
    reader.readAsDataURL(file);
  });
}

function updateFileInput() {
  const dataTransfer = new DataTransfer();
  selectedFiles.forEach(file => dataTransfer.items.add(file));
  document.getElementById('images').files = dataTransfer.files;

  const form = document.querySelector('form');
  form.querySelectorAll('input[name="delete_images"]').forEach(i => i.remove());
  existingImages.forEach(img => {
    if (!img.keep) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'delete_images';
      input.value = img.id;
      form.appendChild(input);
    }
  });
}

