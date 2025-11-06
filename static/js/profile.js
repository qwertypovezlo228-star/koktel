
function toggleCityField() {
	const category = document.getElementById('category').value;
	const cityField = document.getElementById('cityField');
	if (category === '2') {
		cityField.style.display = 'block';
	} else {
		cityField.style.display = 'none';
	}
}

document.addEventListener('DOMContentLoaded', function () {
	toggleCityField();

	const mediaInput = document.getElementById('mediaInput');
	const previewContainer = document.getElementById('previewContainer');
	const fileNames = document.getElementById('fileNames');
	let currentFiles = [];

	if (mediaInput) {
		mediaInput.addEventListener('change', function () {
			currentFiles = Array.from(mediaInput.files);
			renderPreviews();
		});
	}

	function renderPreviews() {
		previewContainer.innerHTML = '';
		fileNames.textContent = '';

		if (currentFiles.length) {
			fileNames.textContent = currentFiles.map(f => f.name).join(', ');
		}

		currentFiles.forEach((file, index) => {
			const reader = new FileReader();
			reader.onload = function (e) {
				const ext = file.name.split('.').pop().toLowerCase();
				let previewWrapper = document.createElement('div');
				previewWrapper.style.position = 'relative';
				previewWrapper.style.display = 'inline-block';
				previewWrapper.style.marginRight = '10px';

				let preview;

				if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
					preview = document.createElement('img');
					preview.src = e.target.result;
				} else if (['mp4', 'webm'].includes(ext)) {
					preview = document.createElement('video');
					preview.src = e.target.result;
					preview.controls = true;
				}

				if (preview) {
					preview.style.maxWidth = '150px';
					preview.style.maxHeight = '150px';
					preview.style.borderRadius = '10px';
					preview.style.objectFit = 'cover';
					preview.style.border = '2px solid var(--accent-color)';
					previewWrapper.appendChild(preview);

					let closeBtn = document.createElement('button');
					closeBtn.type = 'button';
					closeBtn.textContent = '×';
					closeBtn.style.position = 'absolute';
					closeBtn.style.top = '2px';
					closeBtn.style.right = '2px';
					closeBtn.style.background = 'rgba(0,0,0,0.5)';
					closeBtn.style.color = 'white';
					closeBtn.style.border = 'none';
					closeBtn.style.borderRadius = '50%';
					closeBtn.style.width = '20px';
					closeBtn.style.height = '20px';
					closeBtn.style.cursor = 'pointer';
					closeBtn.style.fontSize = '16px';
					closeBtn.style.lineHeight = '18px';
					closeBtn.style.padding = '0';

					closeBtn.addEventListener('click', function () {
						currentFiles.splice(index, 1);
						updateFileInput();
						renderPreviews();
					});

					previewWrapper.appendChild(closeBtn);
					previewContainer.appendChild(previewWrapper);
				}
			};
			reader.readAsDataURL(file);
		});
	}

	function updateFileInput() {
		const dataTransfer = new DataTransfer();
		currentFiles.forEach(file => dataTransfer.items.add(file));
		mediaInput.files = dataTransfer.files;
	}

	document.getElementById('uploadForm').addEventListener('submit', function (e) {
		e.preventDefault();

		const form = e.target;
		const formData = new FormData(form);
		const xhr = new XMLHttpRequest();
		const progressFill = document.getElementById('progressFill');
		const progressContainer = document.getElementById('progressContainer');
		const progressText = document.getElementById('progressText');

		progressContainer.style.display = 'block';
		progressFill.style.width = '0%';
		progressText.textContent = window.TRANSLATIONS.uploading;

		xhr.open('POST', form.action, true);

		xhr.upload.addEventListener('progress', function (e) {
			if (e.lengthComputable) {
				const percent = Math.round((e.loaded / e.total) * 100);
				progressFill.style.width = percent + '%';
				progressText.textContent = `${window.TRANSLATIONS.progress} ${percent}%`;
			}
		});

		xhr.onload = function () {
			if (xhr.status === 200) {
				progressText.textContent = window.TRANSLATIONS.uploaded;
				form.reset();
				currentFiles = [];
				previewContainer.innerHTML = '';
				fileNames.textContent = '';
				setTimeout(() => location.reload(), 1000);
			} else {
				progressText.textContent = window.TRANSLATIONS.error_uploading;
			}
		};

		xhr.send(formData);
	});
});

document.addEventListener('DOMContentLoaded', () => {
  const avatarInput = document.getElementById('avatarInput');
  const avatarPreview = document.getElementById('avatarPreview');

  if (avatarInput) {
    avatarInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (e) {
          avatarPreview.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }
});

