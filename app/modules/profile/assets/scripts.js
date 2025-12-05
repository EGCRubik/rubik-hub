// Profile module scripts
// Handles Two-factor authentication (2FA) toggle form submission via fetch

function initProfile2FA() {
	const form = document.getElementById('toggle-2fa-form');
	if (!form) return;

	form.addEventListener('submit', function (e) {
		e.preventDefault();
		const action = form.action;
		const data = new FormData(form);

		fetch(action, {
			method: 'POST',
			body: data,
			credentials: 'same-origin'
		}).then(function (response) {
			if (response.ok) {
				window.location.reload();
			} else {
				response.text().then(function (text) {
					alert('Error: ' + (text || response.status));
				});
			}
		}).catch(function (err) {
			alert('Request failed: ' + err);
		});
	});
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
	try {
		initProfile2FA();
	} catch (e) {
		console.error('Error initializing Profile 2FA script:', e);
	}
});

// Expose init in case of dynamic usage
window.initProfile2FA = initProfile2FA;
