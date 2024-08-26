frappe.pages['user-manual'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'User Manual',
        single_column: true
    });

		
    let parentDiv = $('<div class="card-container"></div>').appendTo(page.body);


    $('<style>')
        .prop('type', 'text/css')
        .html(
            `.card {
                width: 300px;
                border: 1px solid #ccc;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                text-decoration: none;
                color: inherit;
                transition: box-shadow 0.3s ease;
                margin: 10px; 
                display: flex;
                align-items: center;
                background-color: #fff;
            }

            .card-content {
                display: flex;
                width: 100%;
            }

            .card-image {
                width: 90px;
                height: 90px;
                padding:10px;
                margin-right: 10px;
            }

            .card-text {
                flex: 1;
                padding: 16px;
            }

            .card_header {
                padding: 16px;
                text-align: center;
                font-size: 1.5em;
                font-weight: bold;
                background-color:none !important;
                border-bottom:none;
            }

            .card-body {
                padding: 16px;
            }

            .card:hover {
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
                text-decoration: none;
            }

            .pdf-viewer {
                width: 1240px; 
                height: 90vh;
                top: 50px;
                position: relative;
                background: white;
                border: 1px solid #ccc;
                box-sizing: border-box;
            }

            .pdf-viewer iframe {
                width: 100%;
                height: calc(100% - 50px); 
                border: none; 
            }

            .button-container {
                position: absolute;
                width: 97%; 
                display: flex;
                align-items: center;
                top: 0; 
                background: rgba(255, 255, 255, 0.9); 
                z-index: 10; 
                padding: 10px;/
                box-sizing: border-box; 
            }

            .button-container .button {
                background-color: #000;
                color: white;
                margin-top: 0; 
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                box-sizing: border-box; 
            }

            .button-container .button:hover {
                background-color: #333;
            }

            .button-container .download-button {
                margin-right: auto; 
            }

            /* Flexbox layout for card container */
            .card-container {
                width: 92%;
                display: flex;
                flex-wrap: wrap; 
                justify-content: flex-start; 
                gap: 10px
                padding: 10px;
            }

            /* Back button styling */
            .back-button {
                width: 30px; 
                height: 30px;
                margin-right: 10px;
            }

            /* Back text styling */
            .back-text {
                font-size: 1.2em; /* Adjust text size as needed */
                cursor: pointer;
            }
        `)
        .appendTo('head');

    function createCard(employee) {
        let employeeName = employee.user_manual_name;
        let card = document.createElement('a');
        card.href = '#'; 
        card.className = 'card';
        card.setAttribute('data-pdf-url', employee.attachment); 
        
        let cardContent = document.createElement('div');
        cardContent.className = 'card-content';

       
        let img = document.createElement('img');
        img.src = '/files/user-guide.png'; 
        img.className = 'card-image';
        
        
        let textContainer = document.createElement('div');
        textContainer.className = 'card-text';
        
        let cardHeader = document.createElement('div');
        cardHeader.className = 'card_header';
        cardHeader.textContent = employeeName;
        
        textContainer.appendChild(cardHeader);

        cardContent.appendChild(img);
        cardContent.appendChild(textContainer);

        card.appendChild(cardContent);

        return card;
    }

    function createPdfViewer(pdfUrl, pdfName) {
        let pdfViewer = document.createElement('div');
        pdfViewer.id = 'pdf-viewer';

        let buttonContainer = document.createElement('div');
        buttonContainer.className = 'button-container';

        
        let backButton = document.createElement('img');
        backButton.src = '/files/back-button.png'; 
        backButton.className = 'back-button'; 
        backButton.style.cursor = 'pointer';
        backButton.onclick = () => {
            $('#pdf-viewer').hide();
            $('.card').show();
        };

        
        let backText = document.createElement('span');
        backText.className = 'back-text';
        backText.textContent = 'Back';
        backText.onclick = () => {
            $('#pdf-viewer').hide();
            $('.card').show();
        };

       
        buttonContainer.appendChild(backButton);
        buttonContainer.appendChild(backText);

        pdfViewer.appendChild(buttonContainer);

        let container = document.createElement('div');
        container.className = 'container';

        let iframe = document.createElement('iframe');
        iframe.src = pdfUrl;
        iframe.className = 'pdf-viewer';
        container.appendChild(iframe);

        pdfViewer.appendChild(container);
        return pdfViewer;
    }

    function fetchDataAndCreateCards() {
        frappe.call({
            method: 'ezy_hr.ezy_hr.page.profile_id.profile_id.user_manual',
            callback: function (response) {
                if (response.message && response.message.length > 0) {
                    response.message.forEach(function(employee) {
                        let card = createCard(employee);
                        parentDiv.append(card);
                    });
                } else {
                    frappe.msgprint(__('No data found.'));
                }
            },
            error: function() {
                frappe.msgprint(__('Error fetching data.'));
            }
        });
    }

    fetchDataAndCreateCards();

    parentDiv.on('click', '.card', function() {
        let pdfUrl = $(this).data('pdf-url'); 
        let pdfName = pdfUrl.split('/').pop(); 
        $('#pdf-viewer').remove();
        let pdfViewer = createPdfViewer(pdfUrl, pdfName);
        parentDiv.append(pdfViewer);
        $('.card').hide();
        $('#pdf-viewer').show();
    });
};
	
	