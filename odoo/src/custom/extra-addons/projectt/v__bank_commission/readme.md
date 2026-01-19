Bank Commission
===============

* * *

*   Created by Habib Ouadhour on 7/8/2024
*   [Edit original on dubble](https://dubble.so/guides/bank-commission-uvbp1iaahq2h9898rchh)

* * *

In standard Odoo when you get paid more or less than the invoice amount and you consider that payment as paid.

The difference will be created in a chosen account.

This module will add the possibility to create another line for the bank commission.

> ### 💡 Dependencies
> 
> *   **account:** used to access
>     
>     *   account\_payment, account\_move, account\_move\_line and account\_payment register
>         

Usuage
------

### 1\. Go to your invoice

![](https://dubble-prod-01.s3.amazonaws.com/assets/6299599c-6731-4664-9e59-6a90e21bc013.png?1)

### 2\. Click on ENREGISTRER UN PAIEMENT

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/900b0527-c0ab-4278-96a1-f820f02adbe6/2.5/9.6957891246684/15.264293419633?1)

### 3\. Fill in the form

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/c2f78061-0135-42e2-802f-460889bc2c19/1.9274028629857/49.497903653632/0?1)

### 4\. Click on Marquer comme entièrement payé.

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/587000bc-4429-4d7e-b4eb-03d583dcba7f/2/41.916402840763/13.421980929401?1)

> ### 💡 Note
> 
> *   This option will only appear if the amount is not equal to the invoice amount
>     

### [5\. Fill in the form](http://localhost:8069/web?db=v__accounting_15&debug=0#cids=1&menu_id=215&action=225&model=account.move&view_type=form&id=2902)

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/7217986d-231b-4c8b-afc1-89b52c515d0c/2/51.3507315821/15.011081128748?1)

> ### ⚠️ Warning
> 
> *   The amount of the commission can't be negative.
>     
> *   If the amount is null, Odoo will do its job normally.
>     
> *   Commission account and label will be required only the commission amount is not null.
>     

### 6\. Click on CRÉER UN PAIEMENT

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/175a20d0-5df3-450b-bb80-765f217cb185/1.5/51.459171158837/7.1929707774824?1)

### 7\. Check your payment

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/6ff3f0de-edcb-4d49-8272-64d18a7f9b37/1/100/0?1)

### 8\. Click on VUE

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/f78ecd1f-4937-4648-b197-f1d94ecd167f/2.5/46.082559681698/91.043015102481?1)

### 9\. Click on Pièce comptable

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/335d3757-9948-4e2b-84d0-7938c7548617/1.5/0/30.388442943827?1)

### 10\. Check the journal lines

![](https://d3q7ie80jbiqey.cloudfront.net/media/image/zoom/dfaf2951-e62b-4d96-8fe5-8b7564e01141/1.5/5.5493283135107/0?1)
