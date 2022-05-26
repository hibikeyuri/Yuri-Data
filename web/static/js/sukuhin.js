$(function() {
    var info_json = JSON.parse($('#info_json').text());
    var moreinfo_json = JSON.parse($('#moreinfo_json').text());
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            info: info_json,
            moreinfo: moreinfo_json,
            r18: 'エロ',
            nor18: '正常向'
        },
        created: function() {
        },
        methods: {
        },
        computed: {
        }
    });
});