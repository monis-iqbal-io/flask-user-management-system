document.addEventListener("DOMContentLoaded", function() {
  // Global State Variables
    let currentPage = 1;
    const limit = 10;
    let totalPages = 1;
    let searchText = "";

    // DOM References
    const tableBody = document.getElementById("table-body");
    const pageNumbers = document.getElementById("pageNumbers");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");


    // DOM References for FORM
    const addUserBtn = document.getElementById("addUserBtn");
    const userFormContainer = document.getElementById("userFormContainer");
    const formTitle = document.getElementById("formTitle");
    const userIdInput = document.getElementById("userId");
    const emailInput = document.getElementById("email");
    const mobileInput = document.getElementById("mobile");
    const roleIdInput = document.getElementById("role_id");
    const statusInput = document.getElementById("status");
    const saveUserBtn = document.getElementById("saveUserBtn");
    const cancelBtn = document.getElementById("cancelBtn");


    //  FETCH USERS FUNCTION
    function fetchUsers(page) {

        fetch(`/api/users?page=${page}&limit=${limit}&search=${searchText}`)
            .then(response => response.json())
            .then(result => {

                const users = result.data;
                totalPages = result.total_pages;
                currentPage = result.current_page;

                // Clear table before inserting new data
                tableBody.innerHTML = "";

                // Insert rows
                users.forEach(user => {

                    const row = document.createElement("tr");

                    row.innerHTML = `
                        <td>${user.id}</td>
                        <td>${user.email}</td>
                        <td>${user.mobile}</td>
                        <td>${user.role_id}</td>
                        <td>${user.status}</td>
                        <td>
                            <button class="edit-btn">Edit</button>
                            <button class="delete-btn">Delete</button>
                        </td>
                    `;
                    const editBtn = row.querySelector(".edit-btn");
                    const deleteBtn = row.querySelector(".delete-btn");

                    editBtn.addEventListener("click", function() {
                    editUser(user.id);
                });

                    deleteBtn.addEventListener("click", function() {
                    deleteUser(user.id);
                });

                    tableBody.appendChild(row);
                });

                // Render pagination
                renderPageNumbers();

                // Enable / Disable Prev & Next
                prevBtn.disabled = currentPage === 1;
                nextBtn.disabled = currentPage === totalPages;
            })
            .catch(error => {
                console.error("Error fetching users:", error);
            });
    } 



    //RENDER PAGE NUMBERS
    function renderPageNumbers() {

        pageNumbers.innerHTML = "";

        const maxVisible = 5;

        let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);

        if (end - start < maxVisible - 1) {
            start = Math.max(1, end - maxVisible + 1);
        }

        // First Page
        if (start > 1) {
            addPageButton(1);
            if (start > 2) addDots();
        }

        // Middle Pages
        for (let i = start; i <= end; i++) {
            addPageButton(i);
        }

        // Last Page
        if (end < totalPages) {
            if (end < totalPages - 1) addDots();
            addPageButton(totalPages);
        }
    }



    //ADD PAGE BUTTON
    function addPageButton(page) {

        const btn = document.createElement("button");
        btn.textContent = page;

        if (page === currentPage) {
            btn.disabled = true;
        }

        btn.addEventListener("click", () => {
            currentPage = page;
            fetchUsers(currentPage);
        });

        pageNumbers.appendChild(btn);
    }



    //ADD DOTS
    function addDots() {

        const span = document.createElement("span");
        span.textContent = " ... ";
        pageNumbers.appendChild(span);
    }



    // PREVIOUS BUTTON
    prevBtn.addEventListener("click", () => {

        if (currentPage > 1) {
            currentPage--;
            fetchUsers(currentPage);
        }
    });



    // NEXT BUTTON
    nextBtn.addEventListener("click", () => {

        if (currentPage < totalPages) {
            currentPage++;
            fetchUsers(currentPage);
        }
    });



    // SEARCH BUTTON
    searchBtn.addEventListener("click", () => {

        searchText = searchInput.value.trim();
        currentPage = 1;   // Reset to first page on new search
        fetchUsers(currentPage);
    });





    // Create user
    addUserBtn.addEventListener("click" , function(){

        formTitle.textContent = "Add User";

        userIdInput.value = ""; //Empty means CREATE mode
        
        emailInput.value = "";
        mobileInput.value = "";
        roleIdInput.value = "";
        statusInput.value = "";

        userFormContainer.style.display = "block";

        //updated add user button to scroll to form
        userFormContainer.scrollIntoView({behavior:"smooth"});
    });




    // EDIT USER
    function editUser(id) {

    fetch(`/api/users/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("User not found");
            }
            return response.json();
        })
        .then(user => {

            formTitle.textContent = "Edit User";

            userIdInput.value = user.id;
            emailInput.value = user.email;
            mobileInput.value = user.mobile;
            roleIdInput.value = user.role_id;
            statusInput.value = user.status;

            userFormContainer.style.display = "block";
            userFormContainer.scrollIntoView({behavior: "smooth"});
        })
        .catch(error => {
            alert("User not found");
            console.error(error);
        });
    }



   //Cancel button logic
    cancelBtn.addEventListener("click" , function(){
        userFormContainer.style.display = "none";
    });

    //FORM VALIDATION FUNCTION
    function validateForm(email , mobile ,role_id , status){

        let isValid = true;

        //clear previous errors
        document.getElementById("emailError").textContent = "";
        document.getElementById("mobileError").textContent = "";
        document.getElementById("roleError").textContent = "";
        document.getElementById("statusError").textContent = "";


        // Email regex
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if(!emailPattern.test(email)){
        document.getElementById("emailError").textContent = "Enter a valid email address";
        isValid = false;
    }
    // Mobile regex (exactly 10 digits)
    const mobilePattern = /^[0-9]{10}$/;

    if (!mobilePattern.test(mobile)) {
        document.getElementById("mobileError").textContent = "Mobile must be exactly 10 digits";
        isValid = false;
    }

    //Role ID validation (set between 1 & 3)
    const roleNumber = parseInt(role_id);

    if(isNaN(roleNumber) || roleNumber < 1 || roleNumber > 3){
        document.getElementById("roleError").textContent = "Role ID must be between 1 and 3" ;
        isValid = false;
    }

    //status validation 
    if(status !== "active" && status!== "inactive" ){
        document.getElementById("statusError").textContent = "Please select a valid status";
        isValid = false;
    }
    return isValid;
    }

    // SAVE BUTTON
    saveUserBtn.addEventListener("click" , function(){

        const email = emailInput.value.trim();
        const mobile = mobileInput.value.trim()
        const role_id = roleIdInput.value.trim()
        const status = statusInput.value.trim();


        //Validation function
        if(!validateForm(email , mobile , role_id , status)) {
            return; //stop submission if validation fails
        }

        const userId = userIdInput.value;
        //If user already exists UPDATE
        if(userId){
            fetch(`/api/users/${userId}`,{
                method : "PUT",
                headers : {
                    "Content-Type" : "application/json"
                },
                body: JSON.stringify({
                    email : email,
                    mobile : mobile,
                    role_id : role_id,
                    status : status
                })
            })
            .then(response => response.json())
            .then(data => {
                alert("User updated successfully");

                userFormContainer.style.display = "none";
                userIdInput.value = "";
                fetchUsers(currentPage);
            })
            .catch(error => {
                console.error("Error updating user:" , error);
            });
        }
        //create user if not userid
        else{
            fetch("/api/users",{
                method:"POST",
                headers:{
                    "Content-Type" : "application/json"
                },
                body:JSON.stringify({
                    email : email,
                    mobile : mobile,
                    role_id : role_id,
                    status : status
                })
            })
            .then(response => response.json())
            .then(data => {
                
                alert("User created successfully");
                
                userFormContainer.style.display = "none";
                
                fetchUsers(currentPage);
            })
            .catch(error => {
                console.error("Error creating user:", error)
            });
        }
    });


    // delete user
    function deleteUser(id){
        const confirmDelete = confirm("Are you sure you want to delete this user?");


        if(!confirmDelete){
            return;
        }

        fetch(`/api/users/${id}` ,{
            method: "DELETE"
        })
        .then(response => response.json())
        .then(data => {
            alert("User deleted successfully");

            if (currentPage > 1 && tableBody.children.length === 1) {
            currentPage--;
            }
            fetchUsers(currentPage);
        })
        .catch(error => {
            console.error("Error deleting user" , error)
        })
    }



    //INITIAL LOAD
    fetchUsers(currentPage);

    
});