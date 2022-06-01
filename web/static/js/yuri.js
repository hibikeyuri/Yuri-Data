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
                return '/yuris/' + id
            }
        },
        computed: {
        }
    });
});


// var  tableData = [{}, {}, {}];
// var state = {
//     'querySet': tableData,

//     'page': 1,
//     'rows': 5,
//     'window': 5,
// }

// buildTable()

// function pagination(querySet, page, rows) {

//     var trimStart = (page - 1) * rows
//     var trimEnd = trimStart + rows

//     var trimmedData = querySet.slice(trimStart, trimEnd)

//     var pages = Math.round(querySet.length / rows);

//     return {
//         'querySet': trimmedData,
//         'pages': pages,
//     }
// }

// function pageButtons(pages) {
//     var wrapper = document.getElementById('pagination-wrapper')

//     wrapper.innerHTML = ``
// 	console.log('Pages:', pages)

//     var maxLeft = (state.page - Math.floor(state.window / 2))
//     var maxRight = (state.page + Math.floor(state.window / 2))

//     if (maxLeft < 1) {
//         maxLeft = 1
//         maxRight = state.window
//     }

//     if (maxRight > pages) {
//         maxLeft = pages - (state.window - 1)
        
//         if (maxLeft < 1){
//         	maxLeft = 1
//         }
//         maxRight = pages
//     }
    
    

//     for (var page = maxLeft; page <= maxRight; page++) {
//     	wrapper.innerHTML += `<button value=${page} class="page btn btn-sm btn-info">${page}</button>`
//     }

//     if (state.page != 1) {
//         wrapper.innerHTML = `<button value=${1} class="page btn btn-sm btn-info">&#171; First</button>` + wrapper.innerHTML
//     }

//     if (state.page != pages) {
//         wrapper.innerHTML += `<button value=${pages} class="page btn btn-sm btn-info">Last &#187;</button>`
//     }

//     $('.page').on('click', function() {
//         $('#table-body').empty()

//         state.page = Number($(this).val())

//         buildTable()
//     })

// }

// using jqeury to manipulate some tag or element

// function buildTable() {
//     var table = $('#table-body')

//     var data = pagination(state.querySet, state.page, state.rows)
//     var myList = data.querySet

//     for (var i = 1 in myList) {
//         //Keep in mind we are using "Template Litterals to create rows"
//         var row = `<tr>
//                   <td>${myList[i].rank}</td>
//                   <td>${myList[i].first_name}</td>
//                   <td>${myList[i].last_name}</td>
//                   `
//         table.append(row)
//     }

//     pageButtons(data.pages)
// }
