let login = new Vue({
    delimiters: ['[[', ']]'],
    el: '#login',
    data: {
        loginInfo: {},
        loading: false
    },
    methods: {
        login(){

            if(!this.loginInfo.username || !this.loginInfo.password){

                Swal.fire({
                    title: 'Error',
                    text: 'Por favor diligencia toda la información',
                    type: 'error'
                });

            } else{

                this.loader(true);

                let queryString = Object.keys(this.loginInfo).map(key => {

                    return key + '=' + this.loginInfo[key]
                })
                .join('&');

                axios({
                    method: 'post',
                    url: '/login/',
                    data: queryString,
                    headers: {
                        'Content-type': 'application/x-www-form-urlencoded'
                    }
                })
                .then(response => {             
                    sessionStorage.setItem('userinfo', JSON.stringify(response.data));
                    localStorage.setItem('userinfo', JSON.stringify(response.data));
                    this.loader(false);

                    /*document.cookie = "csrftoken=wG2xUInpzPR787Bz8FXDIONSDYoemwW3;domain=http://kf.oim-opc.pre;path=/"
                    document.cookie = "kobonaut=y4rd7ywp5yz57fjmnv1ca8wzpc1in09m;domain=http://kf.oim-opc.pre;path=/"
                    document.cookie = "selectedAssetUid=aJypqscWMCu3J3URaN2JKf;domain=http://kf.oim-opc.pre;path=/"*/

                    location.href = '/proyectos';
                })
                .catch(error => {

                    this.loader(false);
                    Swal.fire({
                        title: 'Error',
                        text: error.response.data.message,
                        type: 'error'
                    });
                });
            }
        },
        loader(status){

            this.loading = status;
        }
    }
})