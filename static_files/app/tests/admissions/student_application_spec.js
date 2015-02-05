describe('student application for admission', function() {
    beforeEach(function() {
        // this assumes you have multi-tenant correctly set up on your local
        // machine such that atlanta.crey.org points to your local server
        browser.get('http://localhost:8000/admissions/application');
    });

    it('should submit application when all required fields completed', function() {

        // ------------- Section 1 of the Application ----------------------
        // Fill out the first section...

        element(by.css("input[name='fname']")).sendKeys("Quentin");
        element(by.css("input[name='mname']")).sendKeys("Duh");
        element(by.css("input[name='lname']")).sendKeys("Donnellan");
        element(by.cssContainingText(".month-control > option", "January")).click();
        element(by.cssContainingText(".day-control > option", "11")).click();
        element(by.cssContainingText(".year-control > option", "1989")).click();
        element(by.css("input[name='street']")).sendKeys("123 Burke Ave.");
        element(by.css("input[name='city']")).sendKeys("New York");
        element(by.cssContainingText("select[name='state'] > option", "New York")).click();
        element(by.css("input[name='zip']")).sendKeys("12345");
        element(by.css("input[name='email']")).sendKeys("student@example.com");
        element(by.cssContainingText("select[name='sex'] > option", "Male")).click();
        element(by.cssContainingText("select[name='family_preferred_language'] > option", "English")).click();
        element(by.cssContainingText("select[name='ethnicity'] > option", "Hispanic/Latino")).click();
        // (custom_field_66) Race
        element(by.cssContainingText("select[name='custom_field_66'] > option", "Asian")).click();
        element(by.cssContainingText("select[name='religion'] > option", "Roman Catholic")).click();
        element(by.cssContainingText("select[name='heard_about_us'] > option", "Radio")).click();
        // (custom_field_70) Will The Applicant Be Authorized To Work In The U.S. 
        // By The First Day Of The Work Study Program?
        element(by.cssContainingText("select[name='custom_field_70'] > option", "Yes")).click();
        element(by.cssContainingText("select[name='lives_with'] > option", "Both Parents")).click();
        // (custom_field_72) Parent's Marital Status
        element(by.cssContainingText("select[name='custom_field_72'] > option", "Married")).click();

        // ------------- Section 2 of the Application ----------------------
        // Open the second section's accordion div
        element(by.css("a[href='#section-1']")).click();

        // Fill out the second section...

        element(by.cssContainingText("select[name='present_school'] > option", "Adamson Middle")).click();
        // (custom_field_73) List All Schools The Student Has Attended In The Last Three Years
        element(by.css("textarea[name='custom_field_73']")).sendKeys("Bla bla bla");
        // (custom_field_74) Describe The Applicant’s Personal Strengths And Weaknesses
        element(by.css("textarea[name='custom_field_74']")).sendKeys("Strengths: Love, Weaknesses: Love");
        // (custom_field_75) Has The Applicant Experienced Any Behavioral Issues Or Demonstrated 
        // Any Violent, Disruptive Or Disrespectful Behavior In School? Please Explain
        element(by.css("textarea[name='custom_field_75']")).sendKeys("Nope");
        // (custom_field_76) Does The Applicant Suffer From Any Serious Illness, Physical Or 
        //Emotional Limitation, Depression, Or Other Mental Illness? Please Explain
        element(by.css("textarea[name='custom_field_76']")).sendKeys("Nope");
        // (custom_field_77) Has The Applicant Ever Been Arrested Or Convicted Of A Crime?
        element(by.cssContainingText("select[name='custom_field_77'] > option", "No")).click();
        // (custom_field_78) Has The Applicant Ever Had A Psycho-Educational Evaluation?
        element(by.cssContainingText("select[name='custom_field_78'] > option", "No")).click();
        // (custom_field_79) Has The Applicant Been Tested For, Or Diagnosed With, A Learning Disability?
        element(by.cssContainingText("select[name='custom_field_79'] > option", "No")).click();
        // (custom_field_80) Has The Applicant Been Tested For, Or Diagnosed With, ADD Or ADHD?
        element(by.cssContainingText("select[name='custom_field_80'] > option", "No")).click();
        // (custom_field_81) Has The Applicant Now Or Ever Been Enrolled In Special Education Classes?
        element(by.cssContainingText("select[name='custom_field_81'] > option", "No")).click();
        // (custom_field_82) Does The Applicant Currently Have, Or Ever Had, An Individual Education Plan (IEP) Or 504 Plan?
        element(by.cssContainingText("select[name='custom_field_82'] > option", "No")).click();


        // ------------- Section 3 of the Application ----------------------
        // Open the third section's accordion div
        element(by.css("a[href='#section-2']")).click();

        // Fill out the third section...

        // (custom_field_84) Number Of Adults Living In Household
        element(by.css("input[name='custom_field_84']")).sendKeys("2");
        // (custom_field_85) Number Of Children Living In Household
        element(by.css("input[name='custom_field_85']")).sendKeys("10");

        // let's just fill out the first emergency contact field, 
        // which is required by the application
        element.all(by.css("input.emergency-fname")).first().sendKeys("Father");
        element.all(by.css("input.emergency-lname")).first().sendKeys("Time");
        element.all(by.css("input.emergency-relationship")).first().sendKeys("father");
        element.all(by.css("input.emergency-street")).first().sendKeys("123 Burke Ave.");
        element.all(by.css("input.emergency-city")).first().sendKeys("New York");
        element.all(by.cssContainingText(".emergency-state > option", "New York")).first().click();
        element.all(by.css("input.emergency-zip")).first().sendKeys("12345");
        element.all(by.css("input.emergency-home-phone")).first().sendKeys("123-456-7890");
        element.all(by.css("input.emergency-email")).first().sendKeys("daddy@example.com");
        element.all(by.css("input.emergency-occupation")).first().sendKeys("Grunt");
        element.all(by.css("input.emergency-employer")).first().sendKeys("The Army");
        element.all(by.css("input.emergency-work-phone")).first().sendKeys("123-456-7890");
        element.all(by.cssContainingText(".emergency-employment-status > option", "Employed")).first().click();
        element.all(by.cssContainingText(".emergency-is-guardian > option", "Yes")).first().click();

        // ------------- Section 4 of the Application ----------------------
        // Open the forth section's accordion div
        element(by.css("a[href='#section-3']")).click();

        // Fill out the fourth section...

        // (custom_field_109) Did You File Your IRS Income Tax?
        element(by.cssContainingText("select[name='custom_field_109'] > option", "No")).click();
        // (custom_field_111) Tax Reporting Filing Status
        element(by.cssContainingText("select[name='custom_field_111'] > option", "Married")).click();


        // ------------- Section 5 of the Application ----------------------
        // Open the fifth section's accordion div
        element(by.css("a[href='#section-4']")).click();

        // Fill out the fifth section...

        // (custom_field_129) Why Do You Want Your Son Or Daughter To Attend Cristo Rey Atlanta Jesuit High School?
        element(by.css("textarea[name='custom_field_129']")).sendKeys("I'm just a robot filling out this form...");
        // (custom_field_130) Why Do You Believe He Or She Would Do Well Here?
        element(by.css("textarea[name='custom_field_130']")).sendKeys("He's lucky...");

        element(by.css("#application-submit-button")).click();

        // the "Application Complete" section should now be displayed
        expect(element(by.css("#app-complete-div")).isDisplayed());

    });
});