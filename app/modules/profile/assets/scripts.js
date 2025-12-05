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
			if (response.redirected) {
				window.location.href = response.url;
				return;
			}
			if (response.ok) {
				// Try to read JSON for optional redirect_url
				response.clone().json().then(function (json) {
					if (json && json.redirect_url) {
						window.location.href = json.redirect_url;
					} else {
						window.location.reload();
					}
				}).catch(function () {
					window.location.reload();
				});
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
