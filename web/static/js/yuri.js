$(function() {
    var yuris_info = JSON.parse($('#yuris_json').text());
    var filters_info = JSON.parse($('#filters_json').text());

    //its a trial for table head render
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

    state =  {
        'querySet': yuris_info,
        'filters': filters_info,
        'page': 1,
        'rows': 20,
        'window': 5
    }

    function pagination(querySet, page, rows) {

        // for data presentation in the page (trimming yuri data)
        var trimStart = (page - 1) * rows
        var trimEnd = trimStart + rows

        var trimmedData = querySet.slice(trimStart, trimEnd)
        // calculate max ceiling pages number
        var pages = Math.ceil(querySet.length / rows)
        // console.log('pages: ', pages)

        return {
            'querySet': trimmedData,
            'pages': pages,
        }
    };
    
    // using jqeury to manipulate some tag or element
    function buildTable() {
        var table = $('#table-body')
        var data = pagination(state.querySet, state.page, state.rows)
        // console.log('Data: ', data)

        const maxpage = data.pages
        if(maxpage < state.page) {
            state.page = maxpage
            data = pagination(state.querySet, maxpage, state.rows)
        }
        // console.log("data total pages: " + data.pages)
        if(state.page == 0) {
            state.page = 1
        }

        var myList = data.querySet

        for (let i=0; i<myList.length; i+=1) {
            //Keep in mind we are using "Template Litterals to create rows"
            var row = `
                    <tr>
                    <td><img class="yuri_icon" src="${myList[i].icon}"></td>
                    <td><a href="/yuris/${myList[i].id}">${myList[i].name}</a></td>
                    <td>${myList[i].author}</td>
                    <td>${myList[i].publisher}</td>
                    <td>${myList[i].carrier}</td>
                    <td>${myList[i].ero}</td>
                    </tr>
                    `
            table.append(row)
        }
        pageButtons(data.pages)
        // console.log(data.pages)
    };

    function pageButtons(pages) {
        var wrapper = document.getElementById('pagination-wrapper')
        wrapper.innerHTML = ''

        //可顯示頁數按鈕的最大數量之計算
        var maxLeft = (state.page - Math.floor(state.window / 2))
        var maxRight = (state.page + Math.floor(state.window / 2))

        if(maxLeft < 1) {
            maxLeft = 1
            maxRight = state.window
        }
        if(maxRight > pages) {
            maxLeft = pages - (state.window - 1)
            maxRight = pages
            if(maxLeft < 1) {
                maxLeft = 1
            }
        }
        
        for(let page=maxLeft; page<=maxRight; page+=1) {
            if(page === state.page) {
                wrapper.innerHTML += `<a href="javascript:void(0);" class="page active">${page}</a>`
                continue  
            }
            wrapper.innerHTML += `<a href="javascript:void(0);" class="page">${page}</a>`
        }

        if(state.page != 1) {
            wrapper.innerHTML = '<a href="javascript:void(0);" class="pagefirst">Previous</a>' + wrapper.innerHTML
        }

        if(state.page != pages) {
            wrapper.innerHTML += '<a href="javascript:void(0);" class="pagelast">Next</a>'
        }

        $(".page").on('click', function() {
            $("#table-body").empty()
            state.page = Number($(this).text())
            buildTable()
        })

        $(".pagefirst").on('click', function() {
            $("#table-body").empty()
            state.page = 1
            buildTable()
        })

        $(".pagelast").on('click', function() {
            $("#table-body").empty()
            state.page = pages
            buildTable()
        })
    }

    buildTable()

    //for different view rows
    $(".select-container").on('change', function() {
        state.rows = Number($(".select-container option:selected").val())
        $("#table-body").empty()
        buildTable()
    })


    //for filters
    var modal = document.querySelector(".modal-container")
    var btn = document.querySelector(".modal-button")
    var span = document.querySelector(".modal-close")

    btn.onclick = function() {
        modal.style.display = "block"
    }

    span.onclick = function() {
        modal.style.display = "none"
    }

    window.onclick = function(event) {
        if(event.target == modal) {
            modal.style.display = "none"
        }
    }

    let modal_content = document.querySelector(".modal-content")
    let render_template = ''

    function buildModal() {
        for(let key in filters_info) {
            render_template += `
            <div class="row">
                <div class="col col-title"><b>${filters_info[key].label}</b></div>
                <div class="col col-content">
            `
            let opts = filters_info[key].options
            for(let i = 0; i < opts.length; i++) {
                render_template += `
                    <input class="form-check-input" type="checkbox" id="check-${opts[i].name}" name="${key}" value="${opts[i].name}"/>
                    <label class="form-check-form" for="check-${opts[i].name}">${opts[i].name}</label>
                `
            }
            render_template += '</div></div>'
        }
    
        $(".modal-content").append(render_template)   
    }
    
    buildModal()

    $(".modal-container").on("change", function() {
        let res = yuris_info
        for(let key in filters_info) {
            let valuechecked = []
            $.each($("input[name='"+key+"']:checked"), function() {
                valuechecked.push($(this).val())
            })
            // console.log(key + ": " + valuechecked)
            if(key !== "genre"){
                res = res.filter(yuri => { return !valuechecked.length || valuechecked.includes(yuri[key]) })
            }
            else {
                // console.log(res[0][key])//['エロ', '同人作品', '年の差']
                // console.log(res[0][key].some(el => valuechecked.includes(el)))
                res = res.filter(yuri => { return !valuechecked.length || yuri[key].some(genre => valuechecked.includes(genre))})
            }
            // console.log(res)
        }
        state.querySet = res
        $("#table-body").empty()
        buildTable()
        // console.log(state.page)
    })
})