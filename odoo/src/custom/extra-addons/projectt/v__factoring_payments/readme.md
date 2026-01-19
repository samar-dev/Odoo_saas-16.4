Factoring Tutorial
==================

* * *

*   Created by Habib Ouadhour on 4/8/2024
*   [Edit original on dubble](https://dubble.so/guides/factoring-tutorial-a5uvcbrhmvenww4hdkk1)

* * *

This document will guide you step by step from the installation, configuration to the usage of the module

Installation
------------

> ### 💡 Tip
> 
> 1.  All links provided in this document are [localhost](http://localhost) , so it won't work for you.
>     
> 2.  Please make sure all the modules of the Tunisian accounting are updated to the latest version before proceeding with this tutorial
>     

### [1\. Go to Odoo](http://localhost:8069/web?db=v__accounting_15#cids=1&action=menu)

![](https://dubble-prod-01.s3.amazonaws.com/assets/a2ac30cd-5334-4eae-96f2-1ce11f222616.png?0)

### [2\. Go to Settings](http://localhost:8069/web?db=v__accounting_15#cids=1&action=menu)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/1c327494-7a69-4989-a38e-e73293eeb347/1/37.000229779412/47.385984427141?0)

### [3\. Click on Comptabilité Tunisienne](http://localhost:8069/web?db=v__accounting_15#cids=1&action=90&model=res.config.settings&view_type=form&menu_id=4)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/c73d1c1f-eed8-4fbf-9ccf-ecd7f79e256a/1/2.5735294117647/23.414905450501?0)

### [4\. Check the factoring module to enable it](http://localhost:8069/web?db=v__accounting_15#cids=1&action=90&model=res.config.settings&view_type=form&menu_id=4)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/c8e6af6e-34c3-4545-8510-f19856995eca/1/14.200367647059/61.912541713014?0)

### [5\. Click on SAUVER](http://localhost:8069/web?db=v__accounting_15#cids=1&action=90&model=res.config.settings&view_type=form&menu_id=4)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/02ace36e-1413-4717-bca3-d3f28f62dfa8/1/1.3655462184874/11.123470522803?0)

> ### 💡 Note
> 
> 1.  Installing this module will add a new sequence to be used as a reference for the factoring payments.
>     
> 2.  You have the ability to modify it.
>     

Sequence Configuration
----------------------

### [6\. Go to Technique](http://localhost:8069/web?db=v__accounting_15#menu_id=4&cids=1&action=90&model=res.config.settings&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/a89008e5-1d06-472c-81d0-ab6ae29d5aea/1/31.808856355042/1.4738598442714?0)

### [7\. Click on Séquences](http://localhost:8069/web?db=v__accounting_15#menu_id=4&cids=1&action=90&model=res.config.settings&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/18e5b70e-64c7-4f55-85cf-d0d14548f9d0/1/31.021041228992/47.000139043382?0)

### [8\. Search for Factoring](http://localhost:8069/web?db=v__accounting_15#menu_id=4&cids=1&action=27&model=ir.sequence&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/bffc6a15-d57b-4f6d-913d-2461cc7fc584/1/98.109243697479/6.2291434927697?0)

### [9\. Click on Factoring Sequence](http://localhost:8069/web?db=v__accounting_15#menu_id=4&cids=1&action=27&model=ir.sequence&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/8afeac44-3329-41c8-97a5-0a9563b7ae2f/1/18.697478991597/19.855394883204?0)

### [10\. Change the prefix to anything else if you like](http://localhost:8069/web?db=v__accounting_15#id=80&menu_id=4&cids=1&action=27&model=ir.sequence&view_type=form)

1.  This sequence does not belongs to any company.
    
2.  In case you have multi company you assign this sequence to the first company.
    
3.  Duplicate the sequence (you must use the same code) and assign the second company.
    

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/36d070c8-9ced-4c22-b398-c13a9a73177c/1/52.059840065058/7.1198179158826?0)

### [11\. Click on SAUVEGARDER](http://localhost:8069/web?db=v__accounting_15#id=80&menu_id=4&cids=1&action=27&model=ir.sequence&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/a563fe54-6a1e-40dd-a011-65a9e0249cc4/1/0.84033613445378/10.122358175751?0)

Journal Configuration
---------------------

### [12\. Go to accounting App](http://localhost:8069/web?db=v__accounting_15#cids=1&action=menu)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/052eaeed-c128-48cd-93cc-4fdcc2b56f83/1/62.996487657563/16.240266963293?0)

### [13\. Click on Configuration](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/94114862-3599-4b5a-9a25-ac10211cb625/1/35.837381827731/1.4738598442714?0)

### [14\. Click on Journaux](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/a3ea3ba0-24f7-4f5a-9c35-d02f3a7b818d/1/42.684808298319/43.357202447164?0)

### [15\. Click on CRÉER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/e3d40a81-3687-48bd-bdc3-11e903bee339/1/0.84033613445378/10.122358175751?0)

### [16\. Name your Factoring journal the way you like](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/46b9baaf-5e1a-458f-a02b-6b0c5f64b1c4/1/2.4159663865546/25.917686318131?0)

### [17\. Check Factoring](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/37fd8f19-9657-457b-ac49-4985dbde8739/1/0/35.169372724728?0)

> ### ⚠️ Warning
> 
> 1.  Type must be bank.
>     
> 2.  Check Factoring option (won't be visible if the type is not bank).
>     

### [18\. Click on Factoring Commissions](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/b4e1dda4-667c-46ef-86bb-0ca887371d48/1/31.573332457983/49.694104560623?0)

### [19\. Add your commission lines](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/14d4eee4-7fef-4a9e-a51a-63c0317b9013/1/3.4975709033613/57.018214682981?0)

> ### ⚠️ Warning
> 
> 1.  Leaving it empty it means no commission will be applied.
>     

> ### 💡 Fields definition
> 
> 1.  **Name** used to identify the commission line.
>     
> 2.  **Label** used when we create the journal items.
>     
> 3.  **Value Type** can be an amount or percentage.
>     
> 4.  **Value** depends on the **Value Type** field if it is percentage will be calculated from the total amount of the payments that will be send to factoring.
>     
> 5.  **Account** used when we create the journal item.
>     

> ### ⚠️ Warning
> 
> *   For the **Account** field choose wisely there is no control at all.
>     

### [20\. Define the payment methods](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/b5e074fa-b85b-4371-9190-ec59c0251ba1/1/9.5128676470588/49.694104560623?0)

### [21\. Click on Ajouter une ligne](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/6e4bd96f-fa02-455c-9d87-422b1c02b636/1/3.4975709033613/57.018214682981?0)

### [22\. Click on Chèque](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/09e0793f-5521-421a-b8f7-eac041c71d01/1/3.5763524159664/66.918103448276?0)

### [23\. Choose your "Chèque en coffre" account here.](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/67dd7a42-223d-4658-8bf0-75a0f5044dd2/1/26.002823004202/57.630005561735?0)

### [24\. Click on 4564564564564 En Coffre](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/bdeda2ff-5ab6-42f4-bfe7-a76bf37ebdd8/1/26.055344012605/61.245133481646?0)

### [25\. Choose a sequence code for your journal](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/3dab8153-4f71-49c8-b63f-c35282c1610b/1/8.4876660341556/59.333923219406?0)

### [26\. Click on SAUVEGARDER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/1f59dda6-1395-4776-9b4b-32984fa3874d/1/0.84033613445378/10.122358175751?0)

Create an invoice
-----------------

### [27\. Click on Clients](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/5009abe6-1ad1-4bef-af5c-5c7b69191595/1/16.81903230042/1.4738598442714?0)

### [28\. Click on Factures](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/be08500a-53cb-4e78-8bcf-fca880843acd/1/16.03121717437/5.7842046718576?0)

### [29\. Click on CRÉER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/b4ba152c-1b27-43e4-99ae-3a0545cc02c2/1/0.84033613445378/10.122358175751?0)

### [30\. Click on CONFIRMER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form)

*   After filling the necessary information
    

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/452bae9e-d17c-4bf1-b6d8-84e1e78b2417/1/0/0?0)

### [31\. Click on ENREGISTRER UN PAIEMENT](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2661)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/f323f2c5-b2d5-49e3-80c0-9f26d16f39e4/1/0/0?0)

> ### 💡 Note
> 
> 1.  We will demonstrate that the customer is giving us two separate checks.
>     

### [32\. Click on CRÉER UN PAIEMENT](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2661)

*   After changing the amount and setting the necessary information.
    

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/509f3542-9464-4128-b07e-2255cc15c895/1.5/54.801052679136/0?0)

### [33\. Click on ENREGISTRER UN PAIEMENT (2nd payment)](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2661)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/7d70600d-7f0f-4e63-888e-b227f8a98aa1/2.5/9.5990349264706/15.739710789766?0)

### [34\. Click on CRÉER UN PAIEMENT](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2661)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/b656d637-5b7f-4937-aeb8-c576e8753324/1.5/53.983848378061/0?0)

Factoring Usage
---------------

### [35\. Click on Clients](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2661)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/cb3c20c2-2166-4720-b714-602b9bf3adf9/1/16.81903230042/1.4738598442714?0)

### [36\. Click on Factoring](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2661)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/302b9877-9183-4b0e-9d62-73a4efd838f6/2.5/16.03121717437/17.130144605117?0)

> ### 💡 Note
> 
> 1.  Only user that have at least **Facturation** on the accounting module can use this feature.
>     

### [37\. Click on CRÉER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/6e20ec1b-2a97-4efb-a415-782fd42a7774/1/0.84033613445378/10.122358175751?0)

### [38.](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/95ba6008-fe24-4fbf-a9f1-0e71932b0e3a/1/2.4159663865546/24.860956618465?0)

> ### 💡 Tip
> 
> 1.  You can set anything in the **Number** field.
>     
> 2.  If you leave as default **/** the sequence that we talked about earlier will be used.
>     

### [39\. Choose your Factoring Journal](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/d0c52870-9870-4622-93c2-be1bb74bcbee/1/10.294117647059/32.091212458287?0)

> ### ⚠️ Warning
> 
> 1.  Only Factoring journal will be visible.
>     
> 2.  You don't have the ability to quick create journals from this user interface.
>     
> 3.  Configure your journal beforehand.
>     

### [40\. Choose your customer](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/09ced1e4-82f9-4b4d-9519-d67610acda4c/1/10.294117647059/35.205784204672?0)

> ### 💡 Note
> 
> 1.  Customer will be filled for you later on, when you create you Factoring Check.
>     
> 2.  **Date** used on this user interface will be used when generating the journal Items.
>     

### [41\. Click on Ajouter une ligne](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/fd07eb59-81a0-4922-9222-c7bca2caf258/1/2.4159663865546/48.063820912125?0)

### [42\. Click on SÉLECTIONNER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/fe7a00f8-94cc-470e-8b6a-d1384a9f225b/1/25.682773109244/46.205853726363?0)

### [43\. Click on Commissions to type your amounts](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/6eae01a4-3130-4f8d-91f5-286d2d948b52/1/6.7579766281513/40.545050055617?0)

> ### ⚠️ Commission Warning
> 
> 1.  There is no control over the amounts you type.
>     
>     1.  Which means you can type an amount that is bigger than the total amount.
>         
> 2.  If the commission value is zero, no journal item will be generated.
>     
> 3.  You can't delete commission lines from this user interface.
>     

### [44\. Click on SAUVEGARDER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/cd76abaa-e5c5-4cf9-b24e-6cb3d6a1a953/1/0.84033613445378/10.122358175751?0)

> ### ⚠️ Warning
> 
> *   Fields will become readonly after you move from draft state.
>     
> *   So type carefully.
>     

### [45\. Send Payments to Factoring company](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form&id=1)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/4a58abf9-677e-496a-99a8-4614d6d389b8/1/1.3655462184874/15.850945494994?0)

> ### ⚠️ Warning
> 
> 1.  Once you hit the send button there is no going back, so be **aware.**
>     
> 2.  Once the document move from the draft state the document will become undeletable.
>     
> 3.  For the send button to work successfully.
>     
>     1.  You must select at least one payment.
>         
>     2.  Payments must be checks.
>         
>     3.  Payments must have the journal **Coffre.**
>         
>     4.  Payments must be a customer payment.
>         
>     5.  Payments must be posted.
>         

### [46\. Click on Factoring EC to check for the Journal Entries](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=595&model=account.factoring&view_type=form&id=1)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/64a6db11-bfef-4544-98c4-503cfdb464ab/1/61.344537815126/20.022246941046?0)

### [47\. Click on FACT/2024/04/0001 to go back](http://localhost:8069/web?db=v__accounting_15#id=2664&menu_id=215&cids=1&active_id=1&model=account.move&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/88b9beec-419d-4679-ad3c-e58dfd6a6d80/1/5.4026540051504/45.847608750701?0)

### [48\. Click on FACTORING CHECK](http://localhost:8069/web?db=v__accounting_15#id=1&menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/126d8541-4926-4b66-b291-666284c1a68c/1/2.557937237395/15.739710789766?0)

> ### 💡 Tip
> 
> 1.  Factoring button will be visible only if.
>     
>     1.  The state is pending.
>         
>     2.  The amount of the factoring check is the same as the amount minus the commissions.
>         
> 2.  You can add more than one factoring checks.
>     
> 3.  Please add the factoring payment from this interface for auto reconciliation.
>     

### [49\. Click on AJOUTER after adding your check details.](http://localhost:8069/web?db=v__accounting_15#id=1&menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/23d78d91-a966-4a39-8b3e-79796807ea35/1/26.717601102941/59.988528921023?0)

### [50\. Click on Factoring Checks](http://localhost:8069/web?db=v__accounting_15#id=1&menu_id=215&cids=1&action=595&model=account.factoring&view_type=form)

*   If created a single check, a form view will be opened for you containing the payment.
    
*   If you created more than one single payment, a tree view will be opened for you containing all the payments.
    

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/053154e9-f7e4-4bb8-b539-a06eb01dc9d0/1/61.344537815126/19.966629588432?0)

FAQ
---

> ### 💡 FAQ
> 
> *   Q: Am I allowed to add payments from multiple customers?
>     
> *   A: Yes you are allowed to do as long as they are checks and confirms to the conditions we mentioned earlier.
>     
> *   Q: Am I allowed to delete the original customer payments after I add them to the factoring document?
>     
> *   A: No you are not allowed to do so, unless you remove them from the factoring document.
>     
> *   Q: Is there a possibility to reset the document to draft from pending state?
>     
> *   A: At the moment no, maybe in the future.
>     
> *   Q: I miss typed the Factoring check, what should I do?
>     
> *   A: The recommended way is to reset that payment to draft and then delete it, then re enter the payment again from the factoring document.
>     
> *   Q: Can I mix payments from different companies?
>     
> *   A: No and a **BIG NO !**
>
