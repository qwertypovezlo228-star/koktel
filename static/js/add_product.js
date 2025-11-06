function previewImage(event) {
  const file = event.target.files[0];
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('image-preview');

  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      previewImage.src = e.target.result;
      previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
}

function removeImage() {
  const input = document.getElementById('image');
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('image-preview');

  input.value = '';
  previewImage.src = '';
  previewContainer.style.display = 'none';
}
