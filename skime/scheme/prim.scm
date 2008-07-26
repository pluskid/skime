(define-syntax let
  (syntax-rules ()
    ((let ((var val) ...)
       expr ...)
     ((lambda (var ...)
	expr ...)
      val ...))))
