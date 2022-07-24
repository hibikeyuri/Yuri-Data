$(function() {
    var authors_info = JSON.parse($('#authors_json').text());
 
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            authors: authors_info,
            authorinfo: [{'text': 'id', 'val': 'id'},
                {'text': '作者', 'val': 'author'},
            ]
        },
        methods: {
        },
        computed: {
        }
    });

    function buildTable() {
        var table = $('#table-body')
        console.log('Data: ', authors_info)

        for (let i=0; i<authors_info.length; i+=1) {
            //Keep in mind we are using "Template Litterals to create rows"
            var row = `
                    <tr>
                    <td>${authors_info[i].id}</td>
                    <td><a href="/authors/${authors_info[i].id}">${authors_info[i].name}</a></td>
                    </tr>
                    `
            table.append(row)
        }
    };

    buildTable();

});