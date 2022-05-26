$(function() {
    var yuris_info = JSON.parse($('#yuris_json').text());
    console.log(yuris_info)

    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            yuris: yuris_info,
            yuriinfo: [{'text': '', 'val': ''},
                {'text': '名稱', 'val': 'name'},
                {'text': '作者', 'val': 'author'},
                {'text': '出版社', 'val': 'publisher'},
                {'text': '載體', 'val': 'carrier'},
                {'text': 'R18', 'val': 'r18'}],
            filters: {
                'chkauthor': false,
                'chkpublisher': false,
                'chkr18': false
            },
            diroptions: [
                {'text': '以上', 'val': ''},
                {'text': '整', 'val': ''},
                {'text': '以下', 'val': ''},
            ],
        },
        methods: {
            linkfor: function(id) {
                return '/yuri/' + id
            }
        },
        computed: {
        }
    });
});