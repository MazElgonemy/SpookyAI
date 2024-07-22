window.jsPDF = window.jspdf.jsPDF;

    function saveAsPDF() {
        var doc = new jsPDF();
        var content = document.getElementById("contentToSave");

        doc.html(content, {
            callback: function (doc) {
                doc.save("download.pdf");
            },
            x: 10,
            y: 10
        });
    }