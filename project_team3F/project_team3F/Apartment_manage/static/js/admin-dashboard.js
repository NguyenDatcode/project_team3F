$(function() {
    $(document).on('click', '.menu-load', function(e) {
        e.preventDefault();
        const target = $(this).data('target');

        $('.menu-load').removeClass('menu-active');
        $(this).addClass('menu-active');

        // chọn endpoint theo data-target
        if (target === 'apartment') {
            // tải phần nội dung căn hộ (HTML fragment)
            $('#dynamicContent').load('/api/admin/apartment_content', function(response, status, xhr){
                if (status === "error") {
                    console.error("Load apartment content lỗi:", xhr.status, xhr.statusText);
                    $('#dynamicContent').html('<div class="alert alert-danger">Không thể tải nội dung căn hộ.</div>');
                }
            });
        } else if (target === 'apartment_type') {
            $('#dynamicContent').load('/api/admin/apartment_type_content', function(response, status, xhr){
                if (status === "error") {
                    console.error("Load apartment type content lỗi:", xhr.status, xhr.statusText);
                    $('#dynamicContent').html('<div class="alert alert-danger">Không thể tải nội dung loại căn hộ.</div>');
                }
            });
        }
    });

    // (tuỳ chọn) nếu muốn tự load "Căn hộ" khi vào trang admin-dashboard, bỏ comment:
    // $('.menu-load[data-target="apartment"]').trigger('click');
});
