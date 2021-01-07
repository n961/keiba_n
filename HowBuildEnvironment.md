# 環境構築手順
1. ライブラリアップグレード   
    ```pip install --upgrade pip```   
    ```pip install --upgrade pipenv```   
    

2. 環境作成   
    ```pipenv shell```   
    ```pipenv install```


3. nbdimeの設定（ipynbのdiffをいい感じにしてくれるらしい）  
    ```nbdime config-git --enable --global```  


4. お好みでnbextension   
    ```jupyter contrib nbextension install --user```  
    ```jupyter nbextensions_configurator enable --user```  


5. jupyter起動  
    ```jupyter notebook```

