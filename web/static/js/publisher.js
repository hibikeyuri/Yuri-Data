$(function() {
    console.log("OK")
    var publishers_info = JSON.parse($('#publishers_json').text());
 
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            publishers: publishers_info,
            publisherinfo: [{'text': 'id', 'val': 'id'},
                {'text': '出版社', 'val': 'genre'},
            ]
        },
        methods: {
        },
        computed: {
        }
    });

    function buildTable() {
        var table = $('#table-body')
        console.log('Data: ', publishers_info)

        for (let i=0; i<publishers_info.length; i+=1) {
            //Keep in mind we are using "Template Litterals to create rows"
            console.log(publishers_info[i])
            var row = `
                    <tr>
                    <td>${publishers_info[i].id}</td>
                    <td><a href="/publishers/${publishers_info[i].id}">${publishers_info[i].name}</a></td>
                    </tr>
                    `
            table.append(row)
        }
    };

    buildTable();

});