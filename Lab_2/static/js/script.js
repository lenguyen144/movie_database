
// Lấy các phần tử HTML
const objectSelect = document.getElementById("object-select");
const methodSelect = document.getElementById("method-select");
const getOptions = document.getElementById("get-options");
const getType = document.getElementById("get-type");
const idInputArea = document.getElementById("id-input-area");
const recordId = document.getElementById("record-id");
const formArea = document.getElementById("form-area");
const dynamicForm = document.getElementById("dynamic-form");

const clearButton = document.getElementById("clear-button");


// Định nghĩa các trường dữ liệu của từng đối tượng
const objectFields = {
    actor: [
        { name: "FullName", label: "Full Name", type: "text", required: true },
        { name: "DateOfBirth", label: "Date Of Birth", type: "date" },
        { name: "Nationality", label: "Nationality", type: "text" }
    ],

    director: [
        { name: "FullName", label: "Full Name", type: "text", required: true },
        { name: "DateOfBirth", label: "Date Of Birth", type: "date" },
        { name: "Nationality", label: "Nationality", type: "text" }
    ],

    producer: [
        { name: "CompanyName", label: "Company Name", type: "text", required: true },
        { name: "Country", label: "Country", type: "text" }
    ],

    movie: [
        { name: "Title", label: "Title", type: "text", required: true },
        { name: "Duration", label: "Duration (minutes)", type: "number", required: true },
        { name: "Plot", label: "Plot", type: "textarea" },
        { name: "ReleaseYear", label: "Release Year", type: "number" },
        { name: "ProducerID", label: "Producer ID", type: "number", required: true }
    ],

    genre: [
        { name: "GenreName", label: "Genre Name", type: "text", required: true }
    ],

    quote: [
        { name: "MovieID", label: "Movie ID", type: "number", required: true },
        { name: "ActorID", label: "Actor ID", type: "number", required: true },
        { name: "QuoteText", label: "Quote Text", type: "textarea", required: true }
    ]
};


// Tạo một trường nhập liệu
function createField(field) {
    const container = document.createElement("div");

    const label = document.createElement("label");
    label.textContent = field.label;
    label.htmlFor = field.name;

    let input;

    if (field.type === "textarea") {
        input = document.createElement("textarea");
        input.rows = 4;
    } else {
        input = document.createElement("input");
        input.type = field.type;
    }

    input.id = field.name;
    input.name = field.name;


    container.appendChild(label);
    container.appendChild(input);

    return container;
}


// Tạo form theo đối tượng được chọn
function generateForm() {
    const selectedObject = objectSelect.value;

    dynamicForm.innerHTML = "";

    if (!selectedObject || !objectFields[selectedObject]) {
        return;
    }

    objectFields[selectedObject].forEach(field => {
        dynamicForm.appendChild(createField(field));
    });
}


// Cập nhật giao diện theo HTTP Method
function updateInterface() {
    const method = methodSelect.value;
    const selectedGetType = getType.value;

    // Ẩn tất cả khu vực phụ trước
    getOptions.hidden = true;
    idInputArea.hidden = true;
    formArea.hidden = true;

    if (method === "GET") {
        getOptions.hidden = false;

        if (selectedGetType === "by-id") {
            idInputArea.hidden = false;
        }
    }

    else if (method === "POST") {
        formArea.hidden = false;
    }

    else if (method === "PUT") {
        idInputArea.hidden = false;
        formArea.hidden = false;
    }

    else if (method === "DELETE") {
        idInputArea.hidden = false;
    }

    // Xóa ID khi không cần sử dụng
    if (
        method === "GET" && selectedGetType !== "by-id"
    ) {
        recordId.value = "";
    }

    if (method !== "PUT" && method !== "DELETE" &&
        !(method === "GET" && selectedGetType === "by-id")) {
        recordId.value = "";
    }
}


// Khi thay đổi đối tượng
objectSelect.addEventListener("change", function () {
    generateForm();
    updateInterface();
});


// Khi thay đổi HTTP Method
methodSelect.addEventListener("change", function () {
    getType.value = "";
    recordId.value = "";

    generateForm();
    updateInterface();
});


// Khi thay đổi loại GET
getType.addEventListener("change", updateInterface);



// Xử lý dữ liệu từ form thành JSON
function collectFormData() {
    const selectedObject = objectSelect.value;
    const fields = objectFields[selectedObject];

    const data = {};

    for (const field of fields) {
        const input = document.getElementById(field.name);
        let value = input.value.trim();

        if (value === "") {
            data[field.name] = null;
        } else if (field.type === "number") {
            data[field.name] = Number(value);
        } else {
            data[field.name] = value;
        }
    }

    return data;
}


// Hiển thị kết quả API
function displayResponse(status, data) {
    document.getElementById("status-code").textContent = status;

    document.getElementById("response-message").textContent =
        data?.message || data?.error || "Request completed.";

    document.getElementById("json-response").textContent =
        JSON.stringify(data, null, 4);
}


// Gửi HTTP Request
async function sendRequest() {
    const selectedObject = objectSelect.value;
    const method = methodSelect.value;

    if (!selectedObject || !method) {
        alert("Please select an object and HTTP method.");
        return;
    }

    const baseUrl = `/${selectedObject}s`;
    let url = baseUrl;
    let requestOptions = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    // GET
    if (method === "GET") {
        if (!getType.value) {
            alert("Please select Get All or Get By ID.");
            return;
        }

        if (getType.value === "by-id") {
            if (!recordId.value || Number(recordId.value) <= 0) {
                alert("Please enter a valid ID.");
                return;
            }

            url += `/${recordId.value}`;
        }
    }

    // POST
    else if (method === "POST") {
    requestOptions.body = JSON.stringify(collectFormData());
    }

    // PUT
    else if (method === "PUT") {
        url += `/${recordId.value}`;

        requestOptions.body = JSON.stringify(collectFormData());
    }

    // DELETE
    else if (method === "DELETE") {
        if (!recordId.value || Number(recordId.value) <= 0) {
            alert("Please enter a valid ID.");
            return;
        }

        const confirmed = confirm(
            `Are you sure you want to delete this ${selectedObject}?`
        );

        if (!confirmed) {
            return;
        }

        url += `/${recordId.value}`;
    }

    const sendButton = document.getElementById("send-button");

    try {
        sendButton.disabled = true;
        sendButton.textContent = "Sending...";

        const response = await fetch(url, requestOptions);

        const responseText = await response.text();

        let data;

        try {
            data = responseText ? JSON.parse(responseText) : {};
        } catch {
            data = { message: responseText };
        }

        displayResponse(response.status, data);

    } catch (error) {
        displayResponse("Network Error", {
            error: error.message
        });

    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Send Request";
    }
}


// Nút Send Request
document.getElementById("send-button")
    .addEventListener("click", sendRequest);


// Nút Clear Form
clearButton.addEventListener("click", function () {
    recordId.value = "";

    dynamicForm.querySelectorAll("input, textarea").forEach(input => {
        input.value = "";
    });
});


// Nút Clear Response
document.getElementById("clear-response-button")
    .addEventListener("click", function () {
        document.getElementById("status-code").textContent = "No response";
        document.getElementById("response-message").textContent =
            "Waiting for request...";
        document.getElementById("json-response").textContent = "No data";
    });


// Khởi tạo giao diện
generateForm();
updateInterface();

