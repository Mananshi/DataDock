import 'cypress-file-upload';


/// <reference types="cypress" />

describe('File Upload and Management', () => {

    beforeEach(() => {
        cy.visit('/'); // Assumes the app is running on the base URL
    });

    it('Displays the file upload page with drag-and-drop box and upload button', () => {
        cy.get('.dropzone').should('exist');  // Drag-and-drop box
        cy.contains('Select Files').should('exist');  // Button for selecting files
    });

    it('Uploads a single CSV file and shows progress bar', () => {
        // Intercept upload API call
        cy.intercept('POST', '/upload').as('uploadFile');

        // Simulate file selection and upload
        cy.get('input[type="file"]').attachFile('sample.csv');  // Uses cypress-file-upload plugin

        // Click the upload button
        cy.contains('Upload').click();

        // Check progress bar appearance
        cy.get('.progressBarContainer').should('exist');
        cy.wait('@uploadFile');

        // Validate file appears in list view after upload
        cy.contains('Uploaded Files').should('exist');
        cy.contains('sample.csv').should('exist');
    });

    it('Uploads multiple files with individual progress tracking', () => {
        cy.intercept('POST', '/upload').as('uploadFiles');

        // Attach multiple files
        cy.get('input[type="file"]').attachFile(['sample1.csv', 'sample2.csv']);
        cy.contains('Upload').click();

        // Verify progress bars for each file
        cy.get('.progressBarContainer').should('have.length', 2);
        cy.wait('@uploadFiles');

        // Validate both files appear in the list
        cy.contains('Uploaded Files').should('exist');
        cy.contains('sample1.csv').should('exist');
        cy.contains('sample2.csv').should('exist');
    });

    it('Displays and checks progress percentage for each file', () => {
        cy.intercept('GET', '/progress/*').as('progress');

        // Trigger file upload
        cy.get('input[type="file"]').attachFile('sample.csv');
        cy.contains('Upload').click();

        // Wait for progress check calls and verify progress percentages
        cy.wait('@progress').then(({ response }) => {
            expect(response.body.progress_percentage).to.be.greaterThan(0);
        });

        cy.contains('sample.csv').should('exist');
    });

    it('Previews a file and verifies preview content', () => {
        cy.intercept('GET', '/preview/*').as('fetchPreview');

        // Click preview button
        cy.contains('sample.csv').parent().contains('Preview').click();
        cy.wait('@fetchPreview').then(({ response }) => {
            expect(response.body).to.have.length.at.most(5);  // Verify preview limit of 5 lines
        });

        cy.get('.previewBox').should('contain', 'sample content');  // Replace 'sample content' with actual preview text
    });

    it('Downloads a file and verifies download', () => {
        cy.intercept('GET', '/download/*').as('downloadFile');

        // Click download button
        cy.contains('sample.csv').parent().contains('Download').click();

        cy.wait('@downloadFile').then(({ response }) => {
            expect(response.statusCode).to.eq(200);
            expect(response.headers['content-disposition']).to.include('sample.csv');
        });
    });

    it('Displays file list view correctly after uploading files', () => {
        // Verify uploaded files appear in list view with correct details
        cy.contains('Uploaded Files').should('exist');
        cy.get('.fileList').within(() => {
            cy.get('.fileTile').should('have.length.at.least', 1);
        });
    });

    it('Displays error message for invalid file type', () => {
        // Attach a non-CSV file
        cy.get('input[type="file"]').attachFile('sample.txt');

        // Try uploading and verify error
        cy.contains('Upload').click();
        cy.contains('Only .csv files are allowed').should('exist');
    });
});
