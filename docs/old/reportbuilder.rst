.. _reportbuilder:

Custom Report Builder
=======================

Packaged with every instance of Django-SIS is the custom report builder tool. This tool allows users with permission to easily create custom reports utilizing a drag and drop method. This section will cover how to utilize this tool.


Report Builder Dashboard
--------------------------
Access the admin report builder site (sampleurl/admin/report_builder) and click **reports**. The following report builder dashboard screen appears:

.. image:: /images/reportbuilderdash.png

This dashboard will allow the user to view any reports that have previously been created. Additionally, users will have the option of utilizing the available filter to quickly access, sort, and view previous reports by status, date, and root model.

**Starred Reports** are utilized to mark important reports, or reports that will be frequently generated. Users may quickly sort the dash to view only starred reports by selecting the **View Starred Reports** button located towards the top of the dashboard.

Creating a Report
--------------------
From the report builder main screen described above, select **Add Report** located at the top right-hand corner of the dash. The *Add Report* screen displays- **name** and **root model** (students, applicants, workers, etc.) are required fields.

.. image:: /images/addreportscreen.png

It may also be helpful to include an extended description as shown above to provide other users with a more clear direction of how the report is used. Once the information has been entered, select **Save** Your newly created report will now show as the most recent report in the dash, where you can then edit accordingly: 

.. image:: /images/newreportindash.png

Editing a Report
------------------
All created reports have the option of being edited. Using the newly created report from above, to begin editing, select the pencil icon located under the **Edit** column by the respective report, in this instance: Basic Student-Worker Information.

.. image:: /images/editreportscreen.png

With the **Report Display Fields** tab selected at the top, click and drag the fields from the list of available options located at the bottom-left side of the screen into the empty area located directly to the right while the appropiate tab is still selected. **Save** your selection.

*Note:* The **Expand Related Fields** field located in the box above the current fields list allows users to access expanded fields/information. Selecting one option will generate the expanded fields in the box below where you can then drag and drop into the space available accordingly.

After dragging your specified fields and saving, users then have the option to preview the report by selecting the **Preview Report** tab. This will generate a preview, where users can then export into an Excel/Libre-Calc document, as shown below:

.. image:: /images/previewreport.png

Using the Report Filters Tab
------------------------------
The **Report Filters** option is designed to give users the ability to further refine their data. Refining information functions similiar to editing your report, simply select the **Report Filters** tab and use the available fields list on the bottom left to drag and drop into the empty area. 

Using the example above, consider the use case of a user wanting to pull the student-worker data from before, but only for males working on Mondays.

1. Drag and drop **Working day** and **sex** into the open area as shown below.
2. Under the **value** header, select Monday, and Male accordingly.
3. Click **Save** then enter preview tab to view and download into Excel.

.. image:: /images/reportfilterstab.png

Troubleshooting/FAQ
--------------------------

This section is dedicated to helping you troubleshoot your issues with the report builder. Some of the most common user issues are highlighted in bold for your convenience.

**My preview tab won't show results even though the display fields has fields in it.**

The most common reason for this issue is users forgetting to click on save after they have moved the fields they want into the display tab. Keep in mind, the display tab won't show anything unless you have selected save after dragging in your fields.

Example: If you drag in the fields First Name and Last Name then select save you will see those fields in the preview tab. If you go back, drag other fields but never save, when you go to preview, you will only see First Name and Last Name. Selecting save once more will fix the issue and show all your new fields.

**I'm seeing a number of students who are no longer active. I only want active students to show.**

To only see active students, find the *active* field and drag it into your display fields tab. Save. Next, drag the same *active* field into the **Report Filters** tab and set the Filter Type to Equals and the Value box next to it to True. Select Save.

You will now only see a list of students marked as active in the database.

**I can't find the field I'm looking for.**

The first thing you want to check for is to ensure that you're using the correct *root model*. While we provide you with a myriad of root models to choose from, most often you may find what you're looking for by either using the: student, student worker, or applicant root models. From these root models, you can navigate through a number of fields and expanded fields the easiest.

-There's a search box located on the Fields and Expand Related Fields tab- use this to help you locate fields easier.

**The report isn't applying my filters.**

For filters to work, you need to first check that the same field you want to filter is in the display tab. For example, you can't filter by grade level when grade level isn't in the display tab to start off with- in this case, you wouldn't see any change.

You should also make sure that you are using the correct filter type. Typically, the "equals" or "contains" type is the easiest to use, granted whatever you type into the value field is exactly how it appears in the database.

Ex. filter type "equals" set to Sarah will not show any names of Sara. Filter type "contains" will show both.


**Can you utilize multiple values for the same filter?**

Yes. For example, if you have a list of students with their grade levels and you only want to see Juniors and Seniors, then apply the filter type **in(comma separated)** and for value, type in "Junior,Senior" with no space after the comma. The preview will then show only Juniors and Seniors as was requested. 


