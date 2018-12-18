import {openQuestionnaire} from ../../../../helpers/helpers.js

const TextFieldPage = require('../../../../../generated_pages/mutually_exclusive/mutually-exclusive-textfield.page');
const SummaryPage = require('../../../../../generated_pages/mutually_exclusive/optional-textfield-section-summary.page');

describe('Component: Mutually Exclusive Textfield With Single Checkbox Override', function() {

  beforeEach(function() {
    openQuestionnaire('test_mutually_exclusive.json')
          return browser.get(helpers.navigationLink('Textfield')).click();
        });
  });

  describe('Given the user has entered a value for the non-exclusive textfield answer', function() {
    it('When then user clicks the mutually exclusive checkbox answer, Then only the mutually exclusive checkbox should be answered.', function() {

              // Given
        .get(TextFieldPage.textfield()).type('Blue')
        .getValue(TextFieldPage.textfield()).should.eventually.contain('Blue')

        // When
        .get(TextFieldPage.textfieldExclusiveIPreferNotToSay()).click()

        // Then
        .isSelected(TextFieldPage.textfieldExclusiveIPreferNotToSay()).should.eventually.be.true
        .getValue(TextFieldPage.textfield()).should.eventually.contain('')

        .get(TextFieldPage.submit()).click()

        .get(SummaryPage.textfieldExclusiveAnswer()).stripText().should('have.string', 'I prefer not to say')
        .get(SummaryPage.textfieldExclusiveAnswer()).should('not.have.string', 'Blue');

    });
  });

  describe('Given the user has clicked the mutually exclusive checkbox answer', function() {
    it('When the user enters a value for the non-exclusive textfield answer and removes focus, Then only the non-exclusive textfield answer should be answered.', function() {

              // Given
        .get(TextFieldPage.textfieldExclusiveIPreferNotToSay()).click()
        .isSelected(TextFieldPage.textfieldExclusiveIPreferNotToSay()).should.eventually.be.true

        // When
        .get(TextFieldPage.textfield()).type('Blue')

        // Then
        .getValue(TextFieldPage.textfield()).should.eventually.contain('Blue')
        .get(TextFieldPage.textfieldLabel()).click()
        .isSelected(TextFieldPage.textfieldExclusiveIPreferNotToSay()).should.eventually.be.false

        .get(TextFieldPage.submit()).click()

        .get(SummaryPage.textfieldAnswer()).stripText().should('have.string', 'Blue')
        .get(SummaryPage.textfieldAnswer()).should('not.have.string', 'I prefer not to say');

    });
  });

  describe('Given the user has not clicked the mutually exclusive checkbox answer', function() {
    it('When the user enters a value for the non-exclusive textfield answer, Then only the non-exclusive textfield answer should be answered.', function() {

              // Given
        .isSelected(TextFieldPage.textfieldExclusiveIPreferNotToSay()).should.eventually.be.false

        // When
        .get(TextFieldPage.textfield()).type('Blue')

        // Then
        .getValue(TextFieldPage.textfield()).should.eventually.contain('Blue')
        .isSelected(TextFieldPage.textfieldExclusiveIPreferNotToSay()).should.eventually.be.false

        .get(TextFieldPage.submit()).click()

        .get(SummaryPage.textfieldAnswer()).stripText().should('have.string', 'Blue')
        .get(SummaryPage.textfieldAnswer()).should('not.have.string', 'I prefer not to say');

    });
  });

  describe('Given the user has not answered the non-exclusive textfield answer', function() {
    it('When the user clicks the mutually exclusive checkbox answer, Then only the exclusive checkbox should be answered.', function() {

              // Given
        .getValue(TextFieldPage.textfield()).should.eventually.contain('')

        // When
        .get(TextFieldPage.textfieldExclusiveIPreferNotToSay()).click()
        .isSelected(TextFieldPage.textfieldExclusiveIPreferNotToSay()).should.eventually.be.true

        // Then
        .get(TextFieldPage.submit()).click()

        .get(SummaryPage.textfieldExclusiveAnswer()).stripText().should('have.string', 'I prefer not to say')
        .get(SummaryPage.textfieldExclusiveAnswer()).should('not.have.string', 'Blue');

    });
  });

  describe('Given the user has not answered the question and the question is optional', function() {
    it('When the user clicks the Continue button, Then it should display `No answer provided`', function() {

              // Given
        .getValue(TextFieldPage.textfield()).should.eventually.contain('')
        .isSelected(TextFieldPage.textfieldExclusiveIPreferNotToSay()).should.eventually.be.false

        // When
        .get(TextFieldPage.submit()).click()

        // Then
        .get(SummaryPage.textfieldAnswer()).stripText().should('contain', 'No answer provided');

    });
  });

});
