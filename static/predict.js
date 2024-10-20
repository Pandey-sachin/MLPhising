function submitForm(event) {
  event.preventDefault(); // Prevent the default form submission

  var fileInput = document.getElementById('file');
  var websiteLinkInput = document.getElementById('websiteLink');

  var formData = new FormData();

  // Check for file input or website link
  if (fileInput && fileInput.files.length > 0) {
      // File input is selected
      for (var i = 0; i < fileInput.files.length; i++) {
          formData.append('files', fileInput.files[i]);
      }
  } else if (websiteLinkInput && websiteLinkInput.value.trim() !== '') {
      // Website link is provided
      formData.append('websiteLink', websiteLinkInput.value.trim());
  } else {
      // No valid input provided
      alert('Please provide at least one input (Prediction Batch Files or Website Link).');
      return;
  }

  // Show the loader
  var loader = document.getElementById('loader');
  if (loader) {
      loader.style.display = 'block';
  }

  // Disable the submit button while the request is being processed
  var submitButton = document.querySelector('button[type="submit"]');
  if (submitButton) {
      submitButton.disabled = true;
  }

  // Send the FormData object to the Flask endpoint using Fetch API
  fetch('/predicted/', {
      method: 'POST',
      body: formData
  })
  .then(response => {
      // Check if the response is ok
      if (!response.ok) {
          throw new Error('Error: ' + response.status);
      }

      // Determine content type
      const contentType = response.headers.get('Content-Type');

      // Read the response based on content type
      if (contentType && contentType.indexOf('text/csv') !== -1) {
          // If the response is a CSV file, read it as a Blob
          return response.blob();
      } else {
          // Otherwise, read it as text
          return response.text();
      }
  })
  .then(data => {
      // Hide the loader
      if (loader) {
          loader.style.display = 'none';
      }

      // Enable the submit button
      if (submitButton) {
          submitButton.disabled = false;
      }

      // Clear the form inputs
      if (fileInput) {
          fileInput.value = ''; // Clear file input
      }
      if (websiteLinkInput) {
          websiteLinkInput.value = ''; // Clear website link input
      }

      // Display the response
      var predictionResult = document.getElementById('prediction-result');
      if (predictionResult) {
          predictionResult.style.display = 'block';
      }

      if (data instanceof Blob) {
          // If the response is a Blob (CSV file)
          console.log("Received a file response");
          
          
          // Create a download link for the file
          var fileURL = URL.createObjectURL(data);
          
          
          var downloadButton = document.getElementById('download');
          if (downloadButton) {
            downloadButton.style.display = 'block'; // Show the download button
            downloadButton.onclick = function() {
                var a = document.createElement('a'); // Create a temporary anchor element
                a.href = fileURL; // Set the href to the Blob URL
                a.download = 'Predictions.csv'; // Set the download attribute
                document.body.appendChild(a); // Append to the body
                a.click(); // Trigger the download
                document.body.removeChild(a); // Remove the temporary anchor
            };
        }
      } else {
          // If the response is a text message
          console.log("Received a text response");
          if (predictionResult) {
              predictionResult.innerHTML = data; // Display the text response
          }
      }
  })
  .catch(error => {
      console.error('Error:', error);
      // Hide the loader
      if (loader) {
          loader.style.display = 'none';
      }
      // Enable the submit button
      if (submitButton) {
          submitButton.disabled = false;
      }
  });
}
