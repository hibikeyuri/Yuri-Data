
$(function () {
    var pubsakuhin_info = JSON.parse($('#pub_saku_json').text());
    console.log(pubsakuhin_info)

    buildTable();
    function buildTable() {
        var table = $('#table-body')

        var myList = pubsakuhin_info
        console.log(myList.length)

        for (let i = 0; i < myList.length; i += 1) {
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
            console.log('OK')
        }
    }

})
