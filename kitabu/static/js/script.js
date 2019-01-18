function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  function filterFunction() {
    div = document.getElementById("myDropdown");
    a = div.getElementsByTagName("img");
    for (i = 0; i < a.length; i++) {
        txtValue = a[i].textContent 
        a[i].style.display = "";
    }
  }