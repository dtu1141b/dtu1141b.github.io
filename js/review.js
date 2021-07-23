var table = document.getElementById("table-data").getElementsByTagName('tbody')[0];

function addToTable(e)
{
    var forms = document.querySelector('.form-inline');
    
    if(!forms.checkValidity())
        return false;
    
    event.preventDefault();    

    var name = document.getElementById("input_name").value
    var skill = document.getElementById("input_skill").value 
    var level = document.getElementById("input_level").value
    var arr = [name, skill, level]; 
    
    var row = table.insertRow(table.rows.length);
    for(var i = 0; i < arr.length; i++) {
        var cell = row.insertCell(i);
        cell.innerHTML = arr[i] ;
    }

    document.getElementById("input_name").value = "";
    document.getElementById("input_skill").value = "";
    document.getElementById("input_level").value = "";
}