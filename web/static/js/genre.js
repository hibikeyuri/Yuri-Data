$(function() {
    console.log("OK")
    var genres_info = JSON.parse($('#genres_json').text());
 
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            genres: genres_info,
            genreinfo: [{'text': 'id', 'val': 'id'},
                {'text': '種類', 'val': 'genre'},
            ]
        },
        methods: {
        },
        computed: {
        }
    });

    function buildTable() {
        var table = $('#table-body')
        console.log('Data: ', genres_info)

        for (let i=0; i<genres_info.length; i+=1) {
            //Keep in mind we are using "Template Litterals to create rows"
            console.log(genres_info[i])
            var row = `
                    <tr>
                    <td>${genres_info[i].id}</td>
                    <td><a href="/genres/${genres_info[i].id}">${genres_info[i].name}</a></td>
                    </tr>
                    `
            table.append(row)
        }
    };

    buildTable();

});