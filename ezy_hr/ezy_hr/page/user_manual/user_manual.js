frappe.pages['user-manual'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'User Manual',
        single_column: true
    });
    const mainContainer = $('<div class="main-container"></div>').appendTo(page.body);
    const leftSection = $('<div class="left-section"></div>').appendTo(mainContainer);
    const rightSection = $('<div class="right-section"></div>').appendTo(mainContainer);
    const moduleList = $('<div class="module-list"></div>').appendTo(leftSection);
    const cardContainer = $('<div class="card-container"></div>').appendTo(rightSection);
    appendStyles();
    let collapsedState = {};
    function appendStyles() {
        $('<style>')
            .prop('type', 'text/css')
            .html(`
                .main-container {
                    display: flex;
                    gap: 10px;
                }
                .left-section {
                    flex: 1;
                    max-width: 320px;
                }
                .right-section {
                    flex: 3;
                    padding: 10px;
                    margin-left: 75px;
                    position: relative;
                }
                .module-list {
                    width: 300px;
                    padding: 10px;
                    background-color: #ffffff;
                    box-sizing: border-box;
                    margin-left: -20px;
                }
                .module-header {
                    font-size: 20px;
                    font-weight: bold;
                    margin-top: 20px;
                    cursor: pointer;
                    background-color: #95959526;
                    padding: 10px;
                    border-radius: 15px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .module-header img {
                    width: 24px;
                    height: 24px;
                    margin-left: 20px;
                    transition: transform 0.3s ease;
                    padding: 4px;
                }
                .module-content {
                    display: none;
                    padding-left: 10px;
                }
                .card {
                    width:  280px;
                    border: 1px solid #ccc;
                    border-radius: 15px;
                    overflow: hidden;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    margin: 10px;
                    display: flex;
                    align-items: center;
                    background-color: #fff;
                    transition: box-shadow 0.3s ease;
                    margin-left: -9px;
                }
                .card:hover {
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                    text-decoration: none;
                }
                .card-content {
                    display: flex;
                    width: 100%;
                    height: 60px;
                    align-items: center;
                }
                .card-image {
                    width: 55px;
                    height: 55px;
                    padding: 5px;
                }
                .card-text {
                    flex: 1;
                    padding: 3px;
                    overflow-y: visible ! important ;
                }
                .card_header {
                    font-size: 13px;
                    font-weight: bold;
                    margin: auto;
                    margin-left: 0px;
                }
                .pdf-viewer {
                    width: 100%;
                    height: 90vh;
                    position: absolute;
                    top: 0;
                    left: 0;
                    background: white;
                    border: 1px solid #ccc;
                    z-index: 1000;
                }
                .pdf-viewer iframe {
                    width: 100%;
                    height: calc(100% - 50px);
                    border: none;
                }
                .module-header img.rotate-180 {
                    transform: rotate(180deg);
                }
                .card.selected {
                    border: 2px solid #0000005c;
                }
            `)
            .appendTo('head');
    }
    function createCard(employee) {
        const { user_manual_name: name, attachment: pdfUrl } = employee;
        const card = $('<a class="card"></a>')
            .attr('href', '#')
            .data('pdf-url', pdfUrl);
        const cardContent = $('<div class="card-content"></div>');
        const img = $('<img class="card-image" src="/files/user-guide.png">');
        const textContainer = $('<div class="card-text"></div>');
        const cardHeader = $('<div class="card_header"></div>').text(name);
        textContainer.append(cardHeader);
        cardContent.append(img).append(textContainer);
        card.append(cardContent);
        return card;
    }
    function createModuleSection(moduleName) {
        const moduleSection = $('<div class="module-section"></div>');
        const moduleHeader = $(`<div class="module-header">${moduleName}<img src="/assets/ezy_hr/images/down-arrow.png" class="module-toggle-image"/></div>`);
        const moduleContent = $('<div class="module-content"></div>');
        const toggleImage = moduleHeader.find('.module-toggle-image');
        collapsedState[moduleName] = true;
        moduleHeader.on('click', function () {
            const isCollapsed = moduleContent.is(':hidden');
            const currentlyExpanded = Object.keys(collapsedState).find(name => !collapsedState[name]);
            if (currentlyExpanded && currentlyExpanded !== moduleName) {
                $(`.module-content`).slideUp(100);
                $('.module-header img').removeClass('rotate-180');
                collapsedState[currentlyExpanded] = true;
            }
            if (isCollapsed) {
                moduleContent.slideDown(100);
                toggleImage.addClass('rotate-180');
                collapsedState[moduleName] = false;
                $('#pdf-viewer').remove();
            } else {
                moduleContent.slideUp(100);
                toggleImage.removeClass('rotate-180');
                collapsedState[moduleName] = true;
                $('#pdf-viewer').remove();
            }
        });
        moduleSection.append(moduleHeader).append(moduleContent);
        moduleList.append(moduleSection);
        return moduleContent;
    }
    function createPdfViewer(pdfUrl) {
        const pdfViewer = $('<div id="pdf-viewer"></div>');
        const iframe = $('<iframe></iframe>')
            .attr('src', pdfUrl)
            .addClass('pdf-viewer');
        pdfViewer.append(iframe);
        return pdfViewer;
    }
    function fetchDataAndCreateCards() {
        frappe.call({
            method: 'ezy_hr.ezy_hr.page.profile_id.profile_id.user_manual',
            callback: function (response) {
                if (response.message) {
                    for (const [moduleName, items] of Object.entries(response.message)) {
                        const moduleContent = createModuleSection(moduleName);
                        items.forEach(item => {
                            const card = createCard(item);
                            moduleContent.append(card);
                            card.on('click', function (e) {
                                e.preventDefault();
                                $('.card').removeClass('selected');
                                $(this).addClass('selected');
                                const pdfViewer = createPdfViewer($(this).data('pdf-url'));
                                $('#pdf-viewer').remove();
                                rightSection.append(pdfViewer);
                            });
                        });
                    }
                }
            },
            error: function (error) {
                console.error('Error fetching data:', error);
            }
        });
    }
    fetchDataAndCreateCards();
};
