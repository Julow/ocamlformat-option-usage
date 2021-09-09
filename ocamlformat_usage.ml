;;
#use "topfind"

;;
#require "unix"

;;
#require "astring"

;;
#require "fpath"

open Astring

let read_file path =
  let inp = open_in (Fpath.to_string path) in
  let do_read () =
    let lines = ref [] in
    (try
       while true do
         lines := input_line inp :: !lines
       done
     with End_of_file -> ());
    List.rev !lines
  in
  Fun.protect ~finally:(fun () -> close_in inp) do_read

let parse_opt line =
  let line =
    match String.cut ~sep:"#" line with Some (l', _) -> l' | None -> line
  in
  let opt, value =
    match String.cut ~sep:"=" line with
    | Some (opt, value) -> (String.trim opt, Some (String.trim value))
    | None -> (String.trim line, None)
  in
  if opt = "" then None else Some (opt, value)

let parse_ocamlformat_file name = read_file name |> List.filter_map parse_opt

(** Recursively scan a directory, calls [f acc path] on every files. *)
let rec scan_dir f acc path =
  let path_s = Fpath.to_string path in
  (* Don't scan into symlinks. *)
  match Unix.lstat path_s with
  | { st_kind = S_REG; _ } -> f acc path
  | { st_kind = S_DIR; _ } ->
      let cnames = Sys.readdir path_s in
      Array.fold_left
        (fun acc cname -> scan_dir f acc (Fpath.add_seg path cname))
        acc cnames
  | _ -> acc

let ocamlformat_files =
  scan_dir
    (fun acc path ->
      if Fpath.filename path = ".ocamlformat" then
        (path, parse_ocamlformat_file path) :: acc
      else acc)
    [] (Fpath.v ".")

let () =
  Format.printf "%d .ocamlformat files@\n" (List.length ocamlformat_files);
  let tbl = Hashtbl.create 0 in
  List.iter
    (fun (path, options) ->
      List.iter
        (fun opt ->
          let v =
            match Hashtbl.find_opt tbl opt with Some v -> v | None -> 0
          in
          Hashtbl.replace tbl opt (v + 1))
        options)
    ocamlformat_files;
  Hashtbl.to_seq tbl |> List.of_seq
  |> List.sort (fun (_, a) (_, b) -> b - a)
  |> List.iter (fun ((opt, value), count) ->
         let open Format in
         let pp_value ppf v = fprintf ppf " = %s" v in
         printf "%4d %s%a@\n" count opt (pp_print_option pp_value) value)
