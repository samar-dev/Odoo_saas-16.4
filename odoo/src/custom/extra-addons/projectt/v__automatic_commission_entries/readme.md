v\_\_automatic\_commission\_entries
===================================

* * *

*   Created by Habib Ouadhour on 3/31/2024
*   [Edit original on dubble](https://dubble.so/guides/v-automatic-commission-entries-nljy2hlucow6s3nnujqp)

* * *

This module will allow you to set commission in certain stages.  
After moving from the selected stage an account entry will be created automatically.

> ### 💡 Dependencies
> 
>     1. v__tunisian_accounting
>     2. v__payment_methods_tracking
> 
> 1.  Used for ensuring the user has installed the main module which has the configuration installer.
>     
> 2.  Used to access models defined in the module.
>     
> 3.  Used to access the account models and views.
>     

> ### 💡 Note
> 
> *   Tutorial recorded on [localhost](http://localhost) server, so the links won't work for you.
>     

### [1\. Go to Odoo](http://localhost:8069/web?db=v__accounting_15#cids=1&action=menu)

![](https://dubble-prod-01.s3.amazonaws.com/assets/eeaef2e9-1302-48b2-b2b8-28903e8f970f.png?0)

Configuration
-------------

### [2\. Click on Comptabilité](http://localhost:8069/web?db=v__accounting_15#cids=1&action=menu)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/f25ea06a-523d-4157-ada8-42a0d22d33b4/2.5/63.239867576244/16.240266963293?0)

### [3\. Click on Configuration](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/e8fac729-4a02-4757-b2ab-64f57e0adc88/2.5/36.508493846977/1.4738598442714?0)

### [4\. Click on Journaux](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/3e31e5d6-61af-4235-9892-95be099e6218/2.5/43.484149277689/43.357202447164?0)

### [5\. Select your journal](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=237&model=account.journal&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/21dc0ed5-8d17-462d-b4aa-2ab5b37885bb/2.5/0/37.662775025565?0)

### [6\. Click on Paiements Entrants](http://localhost:8069/web?db=v__accounting_15#id=7&menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/c7913af4-b008-4e0b-b92b-f58423681415/2.5/0/38.278124529018?0)

### [7\. Choose the Payment method and hit Modifier](http://localhost:8069/web?db=v__accounting_15#id=7&menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/f4a8c7dc-c33a-46fd-865c-e63b2f01de9e/1/100/100?0)

### [8\. Click on Commission](http://localhost:8069/web?db=v__accounting_15#id=7&menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/ce848401-b097-497a-9776-9cc10b15c27d/1/50.259445278655/9.8184306599122?0)

### [9\. Click on Ajouter une ligne](http://localhost:8069/web?db=v__accounting_15#id=7&menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

*   Add how many commission line you would like to add.
    

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/0992045b-c75f-46aa-b70a-4c2ecfa37c76/1/46.650280898876/0?0)

> ### 💡 Note
> 
> *   Name is the name of your commission just FYI.
>     
> *   Label will be used as label for the journal items created.
>     
> *   Value type can be an amount or percentage.
>     
>     *   Percentage will computed based on the amount of the payment.
>         
> *   Value you can leave it as it is or you can set a predefined value to help you in the future.
>     
> *   Account will be used when we create the journal item, either a credit account or debit account depends on the payment type.
>     

> ### ⚠️ Warning
> 
> *   There are no control over the accounts, so choose your account wisely.
>     
> *   You can pass the same account for all the commission lines, so be aware of that.
>     
> *   Account is a required field so you can't leave it empty
>     

### [10\. Click on APPLY](http://localhost:8069/web?db=v__accounting_15#id=7&menu_id=215&cids=1&action=237&model=account.journal&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/1861ef5b-c00f-4b5e-a038-b0ff6e3b456f/1/45.079445623846/0.7592714237541?0)

Create an invoice
-----------------

### [11\. Click on Comptabilité](http://localhost:8069/web?db=v__accounting_15#cids=1&action=menu)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/0e054c3e-63e7-4956-bba1-902ba258142f/2.5/63.239867576244/16.240266963293?0)

### [12\. Click on Clients](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/c12a790b-4085-4be8-9f28-0d3995fb00d1/2.5/10.553350290823/0?0)

### [13\. Click on Factures](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=262&model=account.journal&view_type=kanban)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/8c9378e0-0495-498c-9379-80c7587b9748/2.5/16.331427233815/5.7842046718576?0)

### [14\. Click on CRÉER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/db4de0f8-7f2a-4689-892c-84fcfd6c3747/2.5/0.85607276618513/10.122358175751?0)

### [15\. Click on SAUVEGARDER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form)

After filling the necessary information

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/65af0a7e-4b8a-4a2e-b5e0-8509ea0ca272/1/0/0?0)

### [16\. Click on CONFIRMER](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2473)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/7996c19b-053a-41be-aa75-25ecb2c82d4a/2.5/1.3911182450508/15.739710789766?0)

### [17\. Click on ENREGISTRER UN PAIEMENT](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2473)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/4b60040b-ef22-433e-94fb-a18f2ae56d01/2.5/9.7787921348315/15.739710789766?0)

### [18\. Click on Effet](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2473)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/36477b65-45da-43ba-94e2-9c122a28fe59/2.5/32.771535580524/21.078976640712?0)

### [19\. Fill your information of the payment](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2473)

for the due date must be in the future to become escompte, the create your payment

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/6404373e-e922-472f-89d3-9d591c2faa6f/1/0/0?0)

Create Batch Payment
--------------------

### [20\. Click on Clients](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2473)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/62e35f3f-a124-4cc7-8cc8-ffe0978079ea/2.5/17.133995452113/1.4738598442714?0)

### [21\. Click on Paiements](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=225&model=account.move&view_type=form&id=2473)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/f876f72a-76dd-4923-9868-285789e2a825/2.5/16.331427233815/11.457174638487?0)

### [22\. Click on Coffre](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=202&model=account.payment&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/7317eba8-4fdc-4358-bb62-48a09e01ef2f/2.5/0/0.54071396525323?0)

### [23\. Click on ​](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=202&model=account.payment&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/41fef6f9-a613-43d0-b819-cc7655f69c2e/2.5/0/12.530636751373?0)

### [24\. Click on Action](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=202&model=account.payment&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/ec97bb21-5d37-4b74-a10b-c95a6adcb1fb/2.5/44.947089827232/2.1498464243049?0)

### [25\. Click on Créer un Paiement par Borderau](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=202&model=account.payment&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/0eb407a4-843d-428b-aa60-3bf0e03e7fb3/2.5/50.98858012306/25.806451612903?0)

### [26\. Click on MODIFIER](http://localhost:8069/web?db=v__accounting_15#id=131&menu_id=215&cids=1&model=account.batch.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/fce0b52a-2f60-42cc-b966-46b08b8ceaab/2.5/0.85607276618513/10.122358175751?0)

### [27\. Choose your bank journal](http://localhost:8069/web?db=v__accounting_15#id=131&menu_id=215&cids=1&model=account.batch.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/861f1489-7f12-4e8d-8bb7-7721dc9ea814/2.5/28.437667201712/30.033370411568?0)

### [28\. Choose escompte](http://localhost:8069/web?db=v__accounting_15#id=131&menu_id=215&cids=1&model=account.batch.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/acef40a3-dacc-4c44-82c5-b3f1a7fe8acc/1/70.212568390894/32.447705526312?0)

### [29\. Click on VALIDER](http://localhost:8069/web?db=v__accounting_15#id=131&menu_id=215&cids=1&model=account.batch.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/03bfde0f-2c31-40f7-9913-e4d72b56a927/2.5/0/13.86189458941?0)

Process your payment
--------------------

### [30\. Click on Clients](http://localhost:8069/web?db=v__accounting_15#id=131&menu_id=215&cids=1&model=account.batch.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/8825ddaf-03cf-49a0-a19d-749fa1549076/2.5/16.277922685928/0?0)

### [31\. Click on Paiements](http://localhost:8069/web?db=v__accounting_15#id=131&menu_id=215&cids=1&model=account.batch.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/1e0de552-9c94-448b-b6d7-5ed235ca2038/2.5/16.331427233815/11.457174638487?0)

### [32\. Click on Bank](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&action=202&model=account.payment&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/a1e8d7b1-7c03-4b4d-a355-8f6453182929/2.5/16.746923488497/19.855394883204?0)

### [33\. Click on Pièce comptable](http://localhost:8069/web?db=v__accounting_15#id=1834&menu_id=215&cids=1&action=202&model=account.payment&view_type=form)

You can check for the journal items before the creation of the commission

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/c0606f30-170b-4179-8046-41cf54c70ee4/2.5/39.192081326913/23.804226918799?0)

### [34\. Click on ÉTAPE SUIVANTE](http://localhost:8069/web?db=v__accounting_15#id=1834&menu_id=215&cids=1&action=202&model=account.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/337cbc91-ef49-4da5-a4cf-dbb4f19cb199/2.5/11.077113429642/15.739710789766?0)

> ### 💡 Note
> 
> *   We have configured our commission in the actual stage
>     
> *   A new predefined table will appear for you.
>     
> *   If you already set a predefined value will be filled for you automatically.
>     

> ### ⚠️ Warning
> 
> *   You don't have the ability to delete a commission from this interface.
>     
> *   If the commission is not applicable just set the value as zero.
>     
> *   Null values won't be processed, so no journal items for them.
>     

### [35\. Click on APPLIQUER](http://localhost:8069/web?db=v__accounting_15#id=1834&menu_id=215&cids=1&action=202&model=account.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/c00b1979-d40c-46ca-928c-a1fd0459d909/1/25.227394328518/44.577308120133?0)

> ### 💡 Note
> 
> *   If you set at least one commission you will see the history in the payment itself.
>     
> *   Also you can check for the journal items created to check for the expected result.
>     

### [36\. Click on Pièce comptable](http://localhost:8069/web?db=v__accounting_15#id=1834&menu_id=215&cids=1&action=202&model=account.payment&view_type=form)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/db4a9664-e04f-47f1-a34e-913b99a90561/1/0/0?0)

### [37\. Click on BNK1/2024/03/0001](http://localhost:8069/web?db=v__accounting_15#menu_id=215&cids=1&active_id=1834&model=account.move.line&view_type=list)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/a19c506e-b986-41c9-b1d7-da78d1c0acf7/1/6.2048555377207/6.5628476084538?0)
